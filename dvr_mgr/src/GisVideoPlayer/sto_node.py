# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading

import message
from message import *
import network
from network import * 
from msg_imgput import *
from msg_ctrl import * 
from fileserv import *
from mediasvr import *
import utils
import stoZone
import loggin
import imgidx

'''
FileServer 定时删除 未成功传输的文件(依据文件名称) 
文件传输结束，及时从临时目录搬走文件

重建idx: 到影像目录下找到 dat,mov文件，生成trp和 .des文件 ，des文件为json格式，记录此影像是否被索引成功，以及影像其他的数据
trp文件采用trpmapfix产生路段匹配文件 .road ,里面包含了所有影像走过的路段信息
所以一个影像必须具备 .trp,.des,.road,.mov四个文件
.des .trp .road 可以在客户端直接转换好，将这些文件通过一次image_put上传到服务器

服务器在每个zone都设置一个tempdir目录，接收文件之后直接更名文件到正确的存储位置，免去了不同zone拷贝的开销
'''

'''
{
	"nodes":{
			"node.1200":{
				"ipaddr_filesvc":"localhost",
				"port_filesvc":12001,
				"ipaddr_mediasvc":"localhost",
				"port_mediasvc":12002,
				"update_interval":10 , 
				"zones": [
					{ "id":"zone1","path":"d:/temp4","tempdir":"d:/temp4","lowater":500,"enable":true}
				]
			}
	},
	"db":{ "name":"stoimage","host":"localhost","port":5432,"user":"postgres","passwd":"111111"}
}
'''


class NodeFileServer(FileServer):
	def __init__(self,name,addr,app):
		FileServer.__init__(self,name,addr)
		self.app = app


	def eventFilePutRequest(self,file):
		print 'eventFilePutRequest'
		digest  =file['digest']
		#检测digest是否存在
		z = self.app.selectZone(file['filesize'])
		
		if not z:
			#zone空间不够
			m = MsgCallReturn(False,Error_FileCreate_Failed,u'zone space too small!')
			file['conn'].sendMessage(m)
			file['conn'].close()
			return
		try:
			#md5 check 数据校验,存在相同diget视为存在，直接忽略
			dbconn = self.app.getDbConn()
			sql ="select count(*) from core_imagefile where degist=%s"
			cr = dbconn.cursor()
			cr.execute(sql,(digest,))
			r = cr.fetchone()[0]
			print 'sql query:',r
			if r > 0:
				m = MsgCallReturn(False,Error_FileCreate_Failed,u'file:%s has existed!'%file['filename'])
				file['conn'].sendMessage(m)
				file['conn'].close()
				return

			#存储文件路径和存储区
			file['zone'] = z
			temp = utils.genTempFileName()			
			file['filebasename'] = temp


			storedir = z.path+'/'+ utils.getToDayStr()
			if not os.path.exists(storedir):
				os.mkdir(storedir)

			file['storedir'] = storedir
			file['finalname'] = os.path.join(storedir,file['filebasename']+".mov")
			filename = file['finalname']
			fd = open(filename,'wb')
			file['fd'] = fd
			file['conn'].sendMessage(MsgCallReturn())
		except:
			traceback.print_exc()
			m = MsgCallReturn(False,Error_FileCreate_Failed,u'File Creating Exception occurred!')
			file['conn'].sendMessage(m)
			file['conn'].close()

	def eventFilePutFinished(self,file):
		import shutil
		FileServer.eventFilePutFinished(self,file)
		z = file['zone']

		tmpbasename = file['filebasename']

		#取消写入dat文件
		#写入dat文件
#		filename = file['storedir'] +'/' + tmpbasename + '.dat'
#		print 'write dat file:',filename
#		fd = open(filename,'wb')
#		cont = base64.decodestring(file['dat'])
#		fd.write(cont)
#		fd.close()
#		utils.setmtime(filename,file['modifytime'])

		#修改mt时间		
		#写入trp文件
		filename = file['storedir'] +'/' + tmpbasename + '.trp'
		fd = open(filename,'wb')
		cont = base64.decodestring(file['trp'])
		fd.write(cont)
		fd.close()
		utils.setmtime(filename,file['modifytime'])
		trp = filename
		utils.setmtime(file['finalname'],file['modifytime'])
		mov = file['finalname']

		if self.app.getConf().get('image_convert',False):
			#update db
			db = self.app.getDbConn()
			sql ="insert into core_imagefileready (node_id,imgpath,status) values(%s,%s,%s)"
			cr = db.cursor()
			cr.execute(sql,(self.app.id,file['finalname'],0))
			db.commit()
			self.app.getLog().debug('image file commit into db:',file['finalname'])
		else: #直接将trp,mov处理并写入数据库
			import imgidx
			imgidx.importImageFile(file['storedir'],file['filebasename'],file['zone'],self.app)

#媒体播放服务器
class NodeMediaServer(MediaServer):
	def __init__(self,name,addr,app):
		MediaServer.__init__(self,name,addr)
		self.app = app

	def getImageFile(self,imageuri):
		#query db for image information
		filepath=''
		try:
			db = self.app.getDbConn()
			sql = "select imgpath,zone,node from core_stonodeimageindex where imgdigest=%s"
			cr = db.cursor()
			cr.execute(sql,(imageuri,))
			r = cr.fetchone()
			if r:
				filepath = r[0]		
		except:
			traceback.print_exc()
		#return 'D:/test_dvr_data/stosync/a.wmv'
		return filepath
	


class NodeServer(NetworkServer):
	def __init__(self,name):
		NetworkServer.__init__(self,name)
		self.id = name
		self.conf = None
		self.zones=[]
		self.dbconn = None
		self.mtxzone = threading.Lock()
		self.log = loggin.Logger('test').addHandler(loggin.stdout()).addHandler(loggin.FileHandler('node_log',subfix='_%Y%m%d.txt'))
		self.db = None

#	def initDB(self,db):
#		import psycopg2 as pg2
#		try:
#			self.dbconn = pg2.connect(host=db['host'],
#								database=db['name'],
#								port=db['port'],
#								user=db['user'],
#								password=db['passwd'])
#
#			sql = "select count(*) from core_stonodeserver where sid=%s"
#			cr = self.dbconn.cursor()
#			cr.execute(sql,(self.id,))
#			r = cr.fetchone()[0]
#			if r == 0: #插入记录
#				#插入node,zones记录
#				sql = ""
#
#		except:
#			return False
#		return True

	def getLog(self):
		return self.log

	def getDbConn(self):
		import psycopg2 as pg2

		if not self.db:
			db = self.conf['db']
			try:
				self.db = pg2.connect(host=db['host'],database=db['name'],port=db['port'],user=db['user'],password=db['passwd'])
			except:
				print traceback.print_exc()
				self.db = None
		return self.db
	

	def main(self,argv):
		conf = utils.loadjson('node.txt')
		if not conf:
			print 'read configuration file failed!'
			return False
		

		self.conf = conf
		self.id = conf['id']

		zones = self.conf['zones']
		for z in zones:
			if z['enable']:
				zone = stoZone.stoZone(self,z['id'],z['path'],z['tempdir'],z['lowater'])
				if zone.load():
					self.zones.append(zone)

		#测试从zone目录的wmv，trp生成记录到数据库，完成即可退出
		if conf['rebuildimages_fromlocal'] == True:
			for z in self.zones:
				imgidx.rebuildImages_fromlocal(z,self)
			return



#		if not self.initDB(conf['db']):
#			print 'Init Database failed!'
#			return False
		#--End Zone configuration
		self.svcfile = NodeFileServer('filesvc',self.conf['filesvc'],self)
		self.addService(self.svcfile)
		self.svcfile.start()

		self.svcmedia = NodeMediaServer('mediasvc',self.conf['mediasvc'],self)
		self.addService(self.svcmedia)
		self.svcmedia.start()

		self.initZones()

		#1.启动索引后台工作线程 
		thread = threading.Thread(target=self.threadBackService)
		thread.start()
		#2.索引服务线程

		if self.conf.get('image_convert',False):
			for n in range(self.conf.get('idxthread',1)):
				thread = threading.Thread(target=self.threadIndexService)
				thread.start()
		
		print '\nNodeServer starting...'
		utils.waitForShutdown()

	def getConf(self):
		return self.conf

	#更新到数据库
	def update(self):
		for z in self.zones:
			z.update()
		
		
	def threadIndexService(self):
		wait = self.conf.get('idxthread_wait',5)
		while True:
			self.buildImageIndex()
			time.sleep(wait)
			
	def threadBackService(self):
		wait = self.conf.get('statusreport_interval',5)
		while  True:
			self.update()
			self.collectNodeStatus()			
			time.sleep(wait)
	
	#发送存储报告到ctrlserver
	def collectNodeStatus(self):		
		conn = NetConnection()
		addr = self.conf['ctrlserver']
		r = conn.connect( addr )
		if not r:
			print 'ctrl server cannot reachable!'
			return
		status = self.hash_status()
		msg = MsgManagement_NodeStatus(status)		
		conn.sendMessage(msg)
		conn.close()
				
	
	def initZones(self):
		import imgidx
		for zone in self.zones:
			imgidx.initZone(zone,self)
		
	def buildImageIndex(self):
		'''
			扫描每个zone，建立影像关系到系统数据库
		'''
		import imgidx		
		for zone in self.zones:
			imgidx.buildImageIndex(zone,self)
	
	#收罗nodeserver当前运行状况	
	def hash_status(self):
		status = {
			"id":self.id,
			'filesvc': self.conf['filesvc'],
			'mediasvc': self.conf['mediasvc'],
			'zones':[],
			'maxconn':0,
			'curconn':0
		}
		for z in self.zones:
			status['zones'].append(z.hash_status())
		return status
		
	def selectZone(self,filesize):
		'''
			挑选一个最优的zone
		'''
		z = None
		self.mtxzone.acquire()
		self.zones.sort(cmp=lambda x,y:cmp(x.freespace,y.freespace)) # 由小到大排序
		
		if len(self.zones):
			z = self.zones[-1]
			print filesize,z.hash_status()
			if z.freespace - z.lowater < filesize:
				z = None
				print 'zone:%s space is not enough!'%(z.id)
		self.mtxzone.release()
		return z


		
if __name__=='__main__':
	NodeServer('node.65').main(sys.argv)
	
	
	
	
	
	
	