# -- coding:utf-8 --


import SocketServer
import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading

#from ConfigParser import ConfigParser
from mutex import mutex as Mutex

'''
class EntityDevice:pass

class AppDevice:pass


class MediaDataType:	
	GPS   = 1
	AUDIO = 2
	VIDEO = 3
	IMAGE = 4
	TEXT = 5
	RAWBLOB = 10
	UNDEFINED = 0xff



class MediaData_Base:
	def __init__(self,mst):
		self.mst = mst
	
	def getType(self):
		return self.mst
	
	def getId(self):
		#这里是获得的module id,subclass必须支持
		return ''
	
class MediaData_Gps(MediaData_Base):
	def __init__(self):
		MediaData_Base.__init__(self,MediaDataTypeu.GPS)		
	
	
class MediaData_Audio(MediaData_Base):
	G7231 = 1
	GSM610 = 2
	PCM8 = 3
	PCM16 = 4
	
	def __init__(self):
		MediaData_Base.__init__(self,MediaDataType.AUDIO)		

class MediaData_Video(MediaData_Base):
	H264 = 1
	JMPEG = 2
	H263 = 3
	MPEG1 = 4
	MPEG2 = 5
	def __init__(self):
		MediaData_Base.__init__(self)
		self.mst = MediaDataType.VIDEO
	
class MediaData_Image(MediaData_Base):
	PNG = 1
	JPEG = 2
	GIF = 3
	BMP = 4
	UNDEFINE = 0xff
	def __init__(self):
		MediaData_Base.__init__(self)
		self.mst = MediaDataType.IMAGE


'''

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
		
	def write(self,bytes):
		try:
			self.handle.sendall(bytes)
		except:
			traceback.print_exc()
	
	def read(self):
		#某些情况将从连接中直接读取 
		pass
	
	def setCodec(self,codec):
		self.codec = codec

#定义设备事件类型
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
		
#事件接收对象	
class DeviceEvent_Sink:
	
	def __init__(self):
		pass
	
	def event(self,e):
		#处理进入的连接，必须先设置解码器对象
		#if e.type == INCOMMING_CONNECTED:
		#	if isinstance(e.conn,DeviceConnection_Tcp):
		#		
		pass

#服务守护,提供某种通信连接的服务
#数据到达将产生消息给关心着	
class DaemonService_Base:
	
	def __init__(self):		
		pass
	
	def newline(self,url,codec=MediaCodec_Null,async= False):
		pass
		
class DaemonService_Tcp(DaemonService_Base,threading):
	#连接进入将自动产生DeviceConnection_Tcp对象，并以 DeviceData_Event传递给接收者(sink),sink必须设置对应的解码器
	#
	def __init__(self,addr,sink,connCLS=DeviceConnection_Base,codecCLS=MediaCodec_Null):
		#@param addr - (host,port)
		#@param sink - 消息接收对象DeviceEvent_Sink的子类
		#@param connCLS - 连接类 DeviceConnection_Tcp的子类
		DaemonService_Base.__init__(self)
		threading.__init__(self)
		self.connCLS = connCLS
		self.codecCLS = codecCLS
		self.sink = sink
		self.addr = addr
		self.cltsocks=[]
		self.lockClientsocks= threading.Lock()
		
		self.initNetwork()
	
	#tcp服务启动 初始化
	def initNetwork(self):		
		self.sockserver = None
		self.sockserver = socket.socket()
		
		try:
			self.sockserver.bind(self.addr)
			self.sockserver.listen(5)
			while True:
				fdr = []
				fdr.append(self.sockserver)
				self.lockClientsocks.acquire()
				for  s in self.cltsocks:
					fdr.append(s)
				self.lockClientsocks.release()
				
				infds,w,e = socket.select(fdr,[],[])
				for s in infds:
					if s == self.sockserver:	#新连接进入
						sock,peer = self.sockserver.accept()
						e = DeviceEvent_Base()
						e.type = DeviceEvent_Base.INCOMMING_CONNECTED
						e.conn = self.connCLS(self) #构建一个连接对象 DeviceConnection_Base
						e.conn.codec = self.codecCLS()	#设置解码器
						e.conn.handle = sock
						sock.conn = e.conn 		#socket 额外的动态属性，便于快速定位关联对象
						self.sink.event(e) 		#通知外部对象  默认 ActiveObject_Manager进行确认
						if e.accept == False: 	#ActiveObject_Manager应用拒绝连接
							sock.close()							
						else:
							self.cltsocks.append(sock) #此刻未进行aobject与sock的关联 添加到 fd_set
						continue
					else:
						try:
							d = s.read(1024)
							if not d:	# null 表示对方请求关闭了
								raise 'error'
						except: # socket connection lost
							self.lockClientsocks.acquire()
							self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
							self.lockClientsocks.release()
							continue
						
						#数据送入sock绑定的DeviceConnection_Base的解码器
						d,retry = s.conn.codec.decode(d) #解析出来的完整的 ActiveObject_ModuleData
						if d:	#有数据包解出来了
							if s.conn.aom:	#已经将连接与aom关联了						
								s.conn.aom.ao.readData(d,s.conn) # 单线路复用 反射到ActiveObject，并让其分派给不同的module
							else:#未关联，所以要将这个包反射到ActiveObject_Manager
								e = DeviceEvent_Base()
								e.type = DeviceEvent_Base.RECVED_DATA
								e.conn = s.conn
								e.data = d		#多个消息集合
								self.sink.event(e) #让ActiveObject_Manager去处理解码出来的消息包
								if e.accept == False: #关联失败，关闭socket
									self.lockClientsocks.acquire()
									self.cltsocks.remove(s)  
									self.lockClientsocks.release()
									continue						
						else: #检查包缓冲是否过大，无效连接应该尽早丢弃
							if retry == False: #缓冲无效了
								self.lockClientsocks.acquire()
								s.close()
								self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
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
		pass
	

class DaemonService_Manager:
	def __init__(self):
		self.services={}
		self.lockServices = threading.Lock()
	
	__instance = None
	@staticmethod
	def instance(cls):
		if __instance == None:
			__instance = DaemonService_Manager()
		return __instance
		
	def addService(self,name,service):
		self.services[name]= service
	
	def getService(self,name):
		return self.service[name]
	


###################################33
#通信参数与解码器映射表
PORTMAP=[
	{'name':'com1','proto':'serial','port':'COM1','host':'','codec':MediaCodec_SerialComm_Gps,'devicetype':'wait for...'},
	]	

###################################33

#class ActiveObject_ModuleData:
#	def __init__(self):		
#		self.data = None 	#
#		self.module = None 	#通道对象

class ActiveObject_Module:
	def __init__(self,parent,type,name=''):
		self.ao = parent
		self.name = name
		self.type  = MediaDataType.UNDEFINED
		self.dataqueue=[] 		#是ActiveObject_Data
		self.conn = None	#连接对象
		self.id = '' 	#模块对象的硬件标示
		self.url = None #连接信息
		
	def connect(self):
		#向外主动连接
		s = DaemonService_Manager.getService('tcp')
		self.conn = s.newline(self,self.url)
		
	def readData(self,data,conn):
		# data is list , must be aobject.MediaData_Base's subclass
		
		for d in data:
			if d.getType()!= self.type:
				return False
			if data.getId()!= self.id:
				return False
			self.dataqueue.append(d)
		conn.aom = self # bind
		return True
	
	def writeData(self,data):
		pass
	
#active object是个应用概念上的设备对象，运行过程中它将缓存此对象的所有
#接收到的数据，等待其它系统访问、冲刷; 但在对实时性要求比较高的情况下
#ActiveObject要主动提交数据到其它的子系统去 
class ActiveObject_Base:
	#系统对象
	def __init__(self,owner):
		#codecCLS 编解码器类
		self.owner = owner
		self.modules = {} #通道集合
		self.lockmodules = threading.Lock()
	
	def initModules(self):
		for m in self.modules:
			m.connect()					
	
	def getModule(self,type):
		m = None
		try:
			m = self.modules[type]
		except:pass
		return m	

	def readData(self,data,conn):
		#@param: data -  多个消息包
		#@return True - 数据匹配到具体的module设备.else False
		r = False
		for m in self.modules:
			if m.readData(data,conn):	#数据只要是归属任何一个module的就okay
				r = True				
		return r

class ActiveObject_Manager(DeviceEvent_Sink):
	def __init__(self,deliverNext):
		self.lockPendingConns = threading.Lock()
		
		sef.pendingConns=[] #未明确的对象
		self.objects=[]	#ao list
		self.lockObjects = threading.Lock()
		
	def event(self,e):
		if e.type == DeviceEvent_Base.INCOMMING_CONNECTED:
			#目标地址验证
			self.lockPendingConns.acquire()
			self.pendingConns.append(e.conn)
			self.lockPendingConns.release()
			
		elif e.type == DeviceEvent_Base.RECVED_DATA:
			self.lockObjects.acquire()
			for o in self.objects:
				# e.data 多个解码出来的消息报
				if o.readData(e.data,e.conn):#连接与AcitiveObject关联上了，之后的数据接收 将直接传递到ActiveObject.readData()					
					break
				else:
					e.accept = False #无法匹配对应的对象				
			self.lockObjects.release()
			#
			self.lockPendingConns.acquire()
			self.pendingConns.remove(e.conn) #从pending对列去除
			self.lockPendingConns.release()
			
#class DtuServer:
#	def __init__(self):		
#		setattr(socket.socket,'conn',None) #应用连接
#
#
#if __name__=='__main__':
#	server = DtuServer()
	
					
	