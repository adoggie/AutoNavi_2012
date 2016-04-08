# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading

import message
from message import *
import network
from network import * 
from msg_ctrl import * 

import utils
import datetime
from dbconn import *

#管理接口
class ManagementService(NetService):
	def __init__(self,name,addr,app):
		NetService.__init__(self,name,addr)
		self.tmpdir='.'
		self.conf = None
		self.addr = addr
		self.app = app
		self.nodes={}
		self.mtxnodes = threading.Condition()
	
	def eventGotMessage(self,msglist,conn):
		for m in msglist:
			self.dispatchMsg(m,conn)
			
	def dispatchMsg(self,m,conn):
		msg = m.getMsg()
#		print msg
		if msg== 'imageput_selectnode_req': #选择node节点
			self.imageput_SelectNodeServer(m,conn)
			return 
		if msg =='mgr_nodestatus':
			node = m.attrs['nodestatus']
			self.nodeReportStatus(node)
			return
		
		#查询路网影像记录
		if msg =='mgr_query_networkimage':
			self.msgmgr_QueryNetwokImage(m,conn)
			return 
	
	def getNodeServer(self,nodeid):
		self.mtxnodes.acquire()
		node = self.nodes.get(nodeid,None)
		self.mtxnodes.release()
		return node
		
		
		db = self.app.getDbConn()
		cr = db.cursor()
		sql = "select * from core_stoNodeServer where sid=%s"
		cr.execute(sql,(nodeid,))
		
		r = fetchoneDict(cr)
		if not r:
			return None
		return r
	
	def getImageRoads(self,imgid):
		db = self.app.getDbConn()
		cr = db.cursor()
		sql = "select * from core_road where image_id=%s"%imgid
		cr.execute(sql)
		r = fetchallDict(cr)
		return r
	
	#查询路网影像
	def msgmgr_QueryNetwokImage(self,m,conn):
		rc = m.attrs['georect']
		wkt =''
		where=''
		print rc
		if rc: #地理相交
			print 'geometry intersects...'
			x,y,w,h = m.attrs['georect']
			wkt = utils.geo_rect2wktpolygon((x,y,w,h))
			case1 = "ST_Intersects(GeometryFromText('%s'),ST_Envelope(GeometryFromText(wkt)) ) "%wkt
			where+=case1
		dbconn = self.app.getDbConn()
		cr = dbconn.cursor()
		
		endtime = m.attrs['endtime']
		starttime = m.attrs['starttime']
		
		duration = endtime - starttime
		dtstart = datetime.datetime.fromtimestamp(starttime)
		dtend = datetime.datetime.fromtimestamp(endtime)
		
		daystart = m.attrs['daystarthour']
		dayend = m.attrs['dayendhour']
		limit = m.attrs['limit']
		sql = "select * from core_imagefile "
		if where:
			sql+=' where '+where 
		sql+=" and starttime between %s and %s and EXTRACT(HOUR from starttime) between %s and %s "
		sql+=" and removed=0 "
		if m['taskid'] != 0 :
			sql+= " and task_id=%s "%m['taskid']
		sql+=" limit %s"%limit
		print sql
		print (dtstart,dtend,daystart,dayend)
		cr.execute(sql,(dtstart,dtend,daystart,dayend))
		#cr.execute(sql)
		#获取记录
		m2 = MsgMgr_QueryResultNetworkImage()
		m2.attrs = m.attrs
		m = m2
		m.attrs['msg'] = 'mgr_queryresult_networkimage'
		results=[]
		while True:
			r = fetchoneDict(cr)
			
			if not r : break
			imgr = ImageRecord_t()
			imgr.id = r['id']
			imgr.imageid = r['uri']
			imgr.starttime = utils.maketimestamp(r['starttime'])
			imgr.duration = r['duration']
			imgr.gpsdata = r['gpsdata']
			imgr.filesize = r['filesize']
			imgr.wkt = r['wkt']
			imgr.nodeid = r['node']
			imgr.digest = r['degist']
			node = self.getNodeServer(r['node'])
			if not node:
				print 'cannt found online-nodeserver!'
				continue
			imgr.nodesvc = node['mediasvc']
			#print imgr.nodesvc, r['duration'],imgr.duration
			roads = self.getImageRoads(r['id'])
			imgr.roads = roads #哈哈哈，吧数据集hash直接当做结果返回

			#影像隶属的计划名称
			if r['task_id']:
				sql = "select name from core_worktask where id=%s"%r['task_id']
				cc = dbconn.cursor()
				cc.execute(sql)

				rr = cc.fetchone()
				if rr:
					imgr.taskname = rr[0]



			#将标记加载
			sql = "select * from core_imagetag where image_id=%s order by time"%(r['id'])
			cc = dbconn.cursor()
			cc.execute(sql)
			while True:
				rr = fetchoneDict(cc)
				if not rr:
					break
				imgr.tags.append({'id':rr['id'],'time':rr['time'],'lon':rr['lon'],'lat':rr['lat'],'type':rr['type']})

			#添加标记总数
			imgr.tagnum = len(imgr.tags)

			results.append( utils.hashobject(imgr) )
		m.attrs['results'] = results
		#print m.attrs
		conn.sendMessage(m) #发送查询记录到imageplayer端
		
		
	#选择一个最佳的 nodeserver
	def imageput_SelectNodeServer(self,m,conn):
		needspace = m.attrs['needspace']
		nodeserver = ()
		nodelist=[]
		self.mtxnodes.acquire()
		try:
			for id,node in self.nodes.items():
				#node上最大剩余空间的zone
				elapsed = time.time() - node['report_time']
				if  elapsed > self.app.getConf().get('node_alivetime',20) : # 20s之内没有注册进来视为无效
					break # pass
				node['zones'].sort(cmp=lambda x,y: cmp(x['freespace'],y['freespace']))
				zone = node['zones'][-1] #最大freespace的zone
				nodelist.append( (node,zone) ) #每个node上最合适的zone
		except:
			traceback.print_exc()
		self.mtxnodes.release()
		
		
		nodelist.sort( cmp=lambda x,y: cmp(x[1]['freespace'],y[1]['freespace']))	
		# [node->zone,...] 排序，最末一个zone空间最大
		if len(nodelist) == 0:
			m = MsgImagePut_SelectNodeResponse() # node 文件传输服务地址
			conn.sendMessage(m)
			return  #没有一个zone注册进来
		#挑一个最空的
		node,zone = nodelist[-1]
		if zone['freespace'] < needspace:
			m = MsgImagePut_SelectNodeResponse() # node 文件传输服务地址
			conn.sendMessage(m)
			return  #没有一个zone注册进来
		m = MsgImagePut_SelectNodeResponse(node['filesvc']) # node 文件传输服务地址
		conn.sendMessage(m)
		
	# stoNodeServer 上报状态进入
	'''
		status = {
			"id":self.id,
			'filesvc': (self.conf['ipaddr_filesvc'],self.conf['port_filesvc']),
			'mediasvc': (self.conf['ipaddr_mediasvc'],self.conf['port_mediasvc']),
			'zones':[]
		}
		status内容作为hash提交进来
	'''
	def nodeReportStatus(self,node):
		self.mtxnodes.acquire()
		self.nodes[node['id']] = node #node状态写入
		node['report_time'] = time.time() #记录登记时间
		self.mtxnodes.release()
		#print self.nodes[node['id']]
		# write nodes into db
		sql = "select id from core_stonodeserver where sid=%s"
		db = self.app.getDbConn()
		cur = db.cursor()
		cur.execute(sql,(node['id'],))
		rs = fetchallDict(cur)
		values=()
		id = 0
		if len(rs) == 0:
			''' insert new'''
			id = utils.getdbsequence_pg(db,'core_stonodeserver_id_seq')
			sql = "insert into core_stonodeserver values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			values=(
				id,
				node['id'],
				datetime.datetime.now(),
				datetime.datetime.now(),
				node['filesvc'][0],node['filesvc'][1],
				node['mediasvc'][0],node['mediasvc'][1],
				node['maxconn'],node['curconn'],
				0,
				datetime.datetime.now()
			)
		else:
			id = rs[0]['id']
			sql = "update core_stonodeserver set livetime=%s,file_ipaddr=%s,file_port=%s,media_ipaddr=%s,media_port=%s," \
				  " maxconn=%s,curconn=%s where id=%s"
			values=(
				datetime.datetime.now(),
				node['filesvc'][0],node['filesvc'][1],
				node['mediasvc'][0],node['mediasvc'][1],
				node['maxconn'],node['curconn'],
				id
			)
	
		cur = db.cursor()
		cur.execute(sql,values)
		db.commit()
		#处理zone
		nodeid = id
		for z in node['zones']:
			sql = "select id from core_stonodezone where sid=%s "
			cr = db.cursor()
			cr.execute(sql,(z['id'],))
			r = fetchoneDict(cr)
			if not r:
				id = utils.getdbsequence_pg(db,'core_stonodezone_id_seq')
				sql = "insert into core_stonodezone values(%s,%s,%s,%s,%s,%s,%s,%s)"
				values=(
					id,
					z['id'],
					nodeid,
					z['maxspace'],
					z['freespace'],
					datetime.datetime.now(),
					z['path'],
					z['lowater']
				)
			else:
				id = r['id']
				sql ="update core_stonodezone set " \
					 "maxspace=%s,freespace=%s,livetime=%s,path=%s,lowater=%s where id=%s"
				values=(
					z['maxspace'],
					z['freespace'],
					datetime.datetime.now(),
					z['path'],
					z['lowater'],
					id
				)
			cr = db.cursor()
			cr.execute(sql,values)
		db.commit()


	def eventConnCreated(self,conn):
		NetService.eventConnCreated(self,conn)
		thread = NetConnThread(conn)
		
	


class CtrlServer(NetworkServer):
	def __init__(self,name='ctrlserver'):

		NetworkServer.__init__(self,name)
		self.id = name
		self.conf = None
		self.dbconn = None

	
	def initDB(self,db):
		import psycopg2 as pg2
		try:
			self.dbconn = pg2.connect(host=db['host'],
								database=db['name'],
								port=db['port'],
								user=db['user'],
								password=db['passwd'])
		except:
			return False
		return True
	
	def getDbConn(self):
		return self.dbconn
	
	def getConf(self):
		return self.conf
	
	def main(self,argv):
		conf = utils.loadjson('ctrl.txt')
		if not conf:
			print 'read configuration file failed!'
			return False
		if not self.initDB(conf['db']):
			print 'Init Database failed!'
			return False
		self.conf = conf

		#--End Zone configuration
		self.svcmgr = ManagementService('management',
										self.conf['service_mgr'],self )
		self.addService(self.svcmgr)
		self.svcmgr.start()
		
		#1.启动索引后台工作线程 
		thread = threading.Thread(target=self.threadBackService)
		print 'ctrlserver starting...'
		#self.test()
		utils.waitForShutdown()
	
	def threadBackService(self):
		while  True:
			time.sleep(1)
			

		
	def test(self):
		fp = open('d:/temp3/a.txt')
		wkt=fp.read()
		fp.close()
		db = self.getDbConn()
		cr = db.cursor()
		sql="select count(*) from core_imagefile  where ST_Intersects(GeometryFromText( \
		'POLYGON((121.26106 31.009505,0.370668 31.009505,0.370668 0.237948,121.26106 0.237948,121.26106 31.009505))'), \
		ST_Envelope(GeometryFromText(%s)) )"
		sql = "select st_astext(ST_Envelope(GeometryFromText(%s)))"
		sql ="select st_astext(ST_Envelope(GeometryFromText(\
			'POLYGON((121.26106 31.009505,0.370668 31.009505,0.370668 0.237948,121.26106 0.237948,121.26106 31.009505))') )) "
		#cr.execute(sql,(wkt,))
		cr.execute(sql)
		r = cr.fetchone()[0]
		print r

		
	def selectZone(self,filesize):
		return zone
		
if __name__=='__main__':
	CtrlServer().main(sys.argv)
	