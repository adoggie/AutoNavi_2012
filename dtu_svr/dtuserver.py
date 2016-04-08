# -- coding:utf-8 --


import sys,os

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import string

from service import *
from aobject  import *
from pycomm.network import *

from pycomm import utils
from pycomm.dbconn import *

##############################################################


#服务类型
class ServiceEntry:
	def __init__(self,name,proto,host,port,codecCLS):
		self.name = name
		self.proto = proto
		self.host = host
		self.port = port
		self.codec =codecCLS
		


class DtuServer(NetworkServer):
	def __init__(self):
		NetworkServer.__init__(self,'dtuserver')
		self.services=[]
		self.sid='' #das id
		self.GM = None
		self.ctrlconn=None #与控制服务器的连接
		self.dbconn = None
		self.aos ={}	# {id:{ao,[module1,..]},..}
		self.mtxaos = threading.Lock()
		

	

	#初始化配置信息 
	def initConfigs(self):
		r = NetworkServer.init(self,'dtuconfig.txt')
		self.sid = self.getConfig().get('sid')
		db = self.getConfig().get('db')
		self.dbconn = utils.initdb_pg(db)
		
		for svc in self.getConfig().get('services',()):
			if not svc['enable']:
				continue
			name,prot,host,port,cls = svc['name'],svc['proto'],svc['host'],svc['port'],svc['codec']
			se = ServiceEntry(name,prot,host,port,cls)
			self.services.append(se)

	def getDBConn(self):
		return self.dbconn

	#初始化所有ao对象	
	def init_data(self):
		db = self.dbconn
		sql = "select * from device_dtu"
		cr = db.cursor()
		cr.execute(sql,(self.sid,))
		r = fetchoneDict(cr)
		while r:
			ao = ActiveObject_Base(r,self)
			ao.initModules(db)
			self.aos[r['id']] = ao
			r = fetchoneDict(cr)

#	def load_ao(self,aoid):
#		try:
#			db = self.dbconn
#			sql = "select * from giscore_activeobject where id=%s"
#			cr = db.cursor()
#			cr.execute(sql,(aoid,))
#			r = fetchoneDict(cr)
#			if not r:
#				return False
#
#			ao = ActiveObject_Base(r,self)
#			ao.initModules(db)
#			self.mtxaos.acquire()
#			self.aos[ao.id] = ao
#			self.mtxaos.release()
#			print 'load ao:',ao.id, ' ok!'
#		except :
#			traceback.print_exc()
#			return False
#		return  True
#
##	由于系统运行管理中对ao进行增删改操作，需要及时通知到das服务器
#	def unload_ao(self,aoid):
#		try:
#			self.mtxaos.acquire()
#			if self.aos.has_key(aoid):
#				ao = self.aos[aoid]
#				del self.aos[aoid]
#				ao.disconnect()
#			self.mtxaos.release()
#			print 'unload ao:',aoid,' ok!'
#		except:
#			traceback.print_exc()


	def init(self):
		r = self.initConfigs()	#配置信息
		r = self.init_data()	#加载所有ao对象
		
		for s in self.services:
			m = __import__(s.codec) #导入解码模块			
			codecCLS = getattr(m,'MediaCodec') #动态获取 解码类			
			svc = DaemonService_Tcp(self,(s.host,int(s.port)),self.aom_event,codecCLS=codecCLS)
			DaemonService_Manager.instance().addService(s.name,svc) #根据名称增加一种服务对象
		#启动与ctrlserver连接
		thread = threading.Thread(target= self.thread_admin)
#		thread.start()
		self.getLog().debug('dtuserver','started',time.asctime())
	
	def recvEvent(self,evt):
		if evt.type == NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				self.dispatch(m,evt.conn)
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			self.ctrlconn = None
	
	
	def connect_ctrlserver(self):
		addr = self.getConfig().get("ctrlserver")
		if not self.ctrlconn:
			conn = NetConnection(recvfunc = self.recvEvent)
			r = conn.connect( addr )
			if not r:
				#self.getLog().warning('cannot connect ctrlserver!')
				return False
			thread = NetConnThread(conn)
			self.ctrlconn = conn
			#发送注册包
			m = MsgDas_Register_2()
			m['id'] = self.getConfig()['sid']
			self.ctrlconn.sendMessage(m)
			
		return True
			
	#后台管理工作线程
	def thread_admin(self):
		while True:
			try:
				self.connect_ctrlserver()
				if self.ctrlconn:
					#发送保活信息包
					m = MsgDas_Keepalive_2()
					#self.ctrlconn.sendMessage(m)
					pass
			except:
				traceback.print_exc()
			time.sleep(2)
			
		
	#设备连接事件处理
	def aom_event(self,e):
		db = self.getDBConn()
		if e.type == DeviceEvent_Base.INCOMMING_CONNECTED:
			pass
		elif e.type == DeviceEvent_Base.DISCONNECTED:
			pass
		elif e.type == DeviceEvent_Base.RECVED_DATA:
			#print 'aom_event.recved_data'
			#print str(e.data)
			m = e.data # MsgAoModule_Base
			conn = e.conn
			if conn.aom:
				#print 'aom found!'
				try:
					conn.aom.ao.readData(m,conn,db)
				except:
					traceback.print_exc()
			else:
				#print 'aom is null'
				self.mtxaos.acquire()				
				for ao in self.aos.values():
					try:
						if ao.readData(m,conn,db):#连接与AcitiveObject关联上了，之后的数据接收 将直接传递到ActiveObject.readData()
							break
					except:
						traceback.print_exc()
						break
				self.mtxaos.release()
			#next.将gps消息和报警消息传递给ctrlserver
	
	#发送消息到控制服务器		
	def sendmsg_ctrlsvr(self,m):
		try:
			self.ctrlconn.sendMessage(m)
		except:
			pass #traceback.print_exc()
	
	def getActiveObject(self,aoid):
		ao = None
		self.mtxaos.acquire()
		ao = self.aos.get(aoid,None)
		self.mtxaos.release()
		return ao


	#接收来自ctrlserver的消息
	def dispatch(self,m,conn):
		try:
			msg = m.getMsg()
			if msg[-2:] =='_5': #发送到设备的命令消息
				ao = self.getActiveObject(m['aoid'])
				if ao:
					ao.sendData(m,self.dbconn)
				else:
					print 'not activeobject found!'
				return
			if msg =='ao_das_load_6': #加载ao
				self.load_ao(m['aoid'])
			if msg =='ao_das_unload_6':#卸载ao
				self.unload_ao(m['aoid'])


		except:
			traceback.print_exc()
		
	def start(self):
		self.init()
		utils.waitForShutdown()
		


if __name__=='__main__':
	DtuServer().start()
	#sys.exit(server.main(sys.argv, "dtuconfig.txt"))

					
	