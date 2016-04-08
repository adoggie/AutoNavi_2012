# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import select
from codec import *

class DeviceConnectionUrl:
	#设备连接地址描述信息
	def __init__(self,host,port,proto='tcp'):
		self.host=host
		self.port=port
		self.proto = proto # tcp,udp,rs232
	
	def __str__(self):
		return "%s:%s:%s"%(self.proto,self.host,self.port)

class DeviceConnection_Base:
	def __init__(self,url=None):
		self.url = url
		self.aom = None #ActiveObject
		self.codec = None		 
		self.handle = None #通信句柄
		self.mid = ''	#模块编号
		self.delta = None
		#2011.6.13 对于有些设备连接上来时候进行注册设备编号，而不用在
		#后续的消息包中每次携带设备编号
		
	def write(self,bytes): pass
	
	def read(self):
		#某些情况将从连接中直接读取 
		pass
	
	def setCodec(self,codec):
		self.codec = codec

class DeviceEvent_Base:
	CONNECTED = 1
	DISCONNECTED = 2
	RECVED_DATA = 3
	SENT_DATA = 4
	INCOMMING_CONNECTED = 5
	UNDEFINED = 0xff
	def __init__(self):
		self.data = None #具体事件数据内容 ActiveObject_Data
		self.type = DeviceEvent_Base.UNDEFINED
		#self.source = None #事件源对象
		self.conn = None #设备连接对象,tcp socket
		self.accept = True
		
	
class DeviceEvent_Sink:
	#事件接收对象
	def __init__(self):
		pass
	
	def event(self,e):
		#处理进入的连接，必须先设置解码器对象
		#if e.type == INCOMMING_CONNECTED:
		#	if isinstance(e.conn,DeviceConnection_Tcp):
		#		
		pass

class DaemonService_Base:
	#服务守护,提供某种通信连接的服务
	#数据到达将产生消息给关心着
	def __init__(self):		
		pass
	
	def newline(self,url,codec=MediaCodec_Null,async= False):
		pass
		
class DaemonService_Tcp(DaemonService_Base,threading.Thread):
	#连接进入将自动产生DeviceConnection_Tcp对象，并以 DeviceData_Event传递给接收者(sink),sink必须设置对应的解码器
	#每个Service绑定一个服务端口，且此service只允许一种数据解码器 
	def __init__(self,addr,sink,codecCLS=MediaCodec_Null,connCLS=DeviceConnection_Base):
		#@param addr - (host,port)
		#@param sink - 消息接收对象DeviceEvent_Sink的子类
		#@param connCLS - 连接类 DeviceConnection_Tcp的子类
		DaemonService_Base.__init__(self)
		threading.Thread.__init__(self)

		self.connCLS = connCLS
		self.codecCLS = codecCLS
		self.sink = sink
		self.addr = addr
		self.cltsocks=[]
		self.lockClientsocks= threading.Lock()
		
		self.sockserver = socket.socket()		
		self.sockserver.bind(self.addr)
		self.sockserver.listen(5)
		
		self.start() #init thread 
	
	def run(self):
		self.initNetwork()
		
	def initNetwork(self):		
		try:
			while True:
				fdr = []
				fdr.append(self.sockserver)
				self.lockClientsocks.acquire()
				for  s in self.cltsocks:
					fdr.append(s)
				self.lockClientsocks.release()
				
				infds,w,e = select.select(fdr,[],[])
				for s in infds:
					if s == self.sockserver: #新连接到达 
						sock,peer = self.sockserver.accept()
						print 'new client come in:',peer
						e = DeviceEvent_Base()
						e.type = DeviceEvent_Base.INCOMMING_CONNECTED
						e.conn = self.connCLS(self)
						e.conn.codec = self.codecCLS()
						e.conn.handle = sock
						#sock.conn = e.conn
						sock.conmgr[sock] = e.conn
						self.sink.event(e) #通知外部对象，ActiveObjectMgr必须匹配到对应的设备
						if e.accept == False: #应用拒绝连接
							sock.close()							
						else:
							self.cltsocks.append(sock) #此刻未进行aobject与sock的关联
						continue
					else:
						#print s.conmgr
						conn = s.conmgr[s]
						try:
							d = s.recv(1024)
							#print len(d),d
							if not d:
								raise Exception('socket break')
						except: # socket connection lost
							traceback.print_exc()
							self.lockClientsocks.acquire()
							s.conmgr.pop(s)
							self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
							self.lockClientsocks.release()
							self.sink.socketlost(conn)
							continue
						
						packets,retry = conn.codec.decode(d,conn) #解析出来的完整的 MediaType.*
						#print 'decode gps packet size:',len(packets)
						if len(packets):
							for d in packets: # d - 指向不同的数据包类型,这些包允许混在同一个连接上接收
								if conn.aom: #已绑定module设备 
									conn.aom.ao.readData(d,conn) # 单线路复用 反射到ActiveObject，并让其分派给不同的module
								else:#未关联，所以要将这个包反射到ActiveObject_Manager
									e = DeviceEvent_Base()
									e.type = DeviceEvent_Base.RECVED_DATA
									e.conn = conn
									e.data = d
									print 'event(e)',unicode(d)
									self.sink.event(e)
									if e.accept == False: #关联失败，关闭socket
										print 'module match failed! Reject'
										retry = False
										break						
						#检查包缓冲是否过大，无效连接应该尽早丢弃
						if retry == False: #缓冲无效或者解码错误
							print 'retry False'
							self.lockClientsocks.acquire()
							s.conmgr.pop(s)
							self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
							s.close()
							self.lockClientsocks.release()
							continue
		except:
			traceback.print_exc()
		pass
	
	
	def newline(self,module,url):
		#主动向外建立tcp连接
		#@param module  MediaDataType.* 通道媒体类型
		#@param codec 解码器 默认的解码器不对数据做任何处理
		#@param async 是否开启异步读的模式,同步方式必须让用户主动在连接对象上调用read()
		#相同的url 返回相同的connection对象
		print 'do not suport so far!'
		return None
	

class DaemonService_Manager:
	def __init__(self):
		self.services={}
		self.lockServices = threading.Lock()

	__instance = None
	@staticmethod
	def instance():
		if DaemonService_Manager.__instance == None:
			DaemonService_Manager.__instance = DaemonService_Manager()
		return DaemonService_Manager.__instance
		
	def addService(self,name,service):
		self.services[name]= service
	
	def getService(self,name):
		return self.services[name]
	

					
	