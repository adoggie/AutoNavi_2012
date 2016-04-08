# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import select
from codec import *
from pycomm import utils


'''
dtu设备通过gprs通信产生问题：
１.dtu连接进入，数据传输几次，dtu端断开，但服务器未收到断开信号，随后dtu再次建立与server的连接
 有时同一个dtu会与服务器同时建立多个连接，随后等待很长时间在select时检测到某些个socket无效，产生异常

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
	uid = utils.UniqueId()
	def __init__(self,url=None):
		self.url = url
		self.aom = None #ActiveObject module
		self.codec = None		 
		self.handle = None #通信句柄
		self.sock = None
		self.mid = ''	#模块编号
		self.delta = None
		self.mtx = threading.Lock()
		self.id = DeviceConnection_Base.uid.next()	#连接id
		
		#2011.6.13 对于有些设备连接上来时候进行注册设备编号，而不用在
		#后续的消息包中每次携带设备编号
	def close(self):
		self.sock.close()
		self.sock = None
		
	def write(self,bytes):
		try:
			self.sock.sendall(bytes)
			return True
		except:
			traceback.print_exc()
			return False
	
	def read(self):
		#某些情况将从连接中直接读取 
		pass
	
	def setCodec(self,codec):
		self.codec = codec

class DeviceEvent_Base:
	CONNECTED = 1
	DISCONNECTED = 3
	RECVED_DATA = 2
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
		
class DaemonService_Tcp(DaemonService_Base):
	#连接进入将自动产生DeviceConnection_Tcp对象，并以 DeviceData_Event传递给接收者(sink),sink必须设置对应的解码器
	#每个Service绑定一个服务端口，且此service只允许一种数据解码器 
	def __init__(self,app,addr,event,codecCLS=MediaCodec_Null,connCLS=DeviceConnection_Base):
		#@param addr - (host,port)
		#@param sink - 消息接收对象DeviceEvent_Sink的子类
		#@param connCLS - 连接类 DeviceConnection_Tcp的子类
		DaemonService_Base.__init__(self)		
		self.app = app
		self.connCLS = connCLS
		self.codecCLS = codecCLS
		self.event = event #接收事件
		self.addr = addr
		self.cltsocks=[]
		self.mtxsocks= threading.Lock()
		
		self.exc_mq = utils.Thread_MQ(self.thread_decode,1)
		
		self.sockserver = socket.socket()		
		self.sockserver.bind(self.addr)
		self.sockserver.listen(5)
		
		thread = threading.Thread(target=self.thread_svc)
		thread.start()
	
	#驱使多个线程执行解码
	def thread_decode(self,conn):
		packets,retry = conn.codec.decode() #解析出来的完整的 MediaType.*					
		if len(packets):
			for d in packets: # d - (MsgAoModule_Base)指向不同的数据包类型,这些包允许混在同一个连接上接收
				e = DeviceEvent_Base()
				e.type = DeviceEvent_Base.RECVED_DATA
				e.conn = conn
				e.data = d
				self.event(e) # route to DtuServer.aom_event()
				if e.accept == False: #关联失败，关闭socket
					print 'Reject'
					retry = False
					break
				
		#检查包缓冲是否过大，无效连接应该尽早丢弃
		if retry == False: #缓冲无效或者解码错误
			conn.close()			
	'''
	问题: dtu的连接丢失之后平台服务器无法通过select获取断开事件，但是dtu在gprs网络
		已经断开，然后dtu再次建立与服务器连接；但之前建立的那个socket连接再后续select
		的时候会抛出异常，所以本来是多fdset一次进行select，先必须改成对每个fd进行select
		检测，并加上timeout字段
	'''
	def thread_svc(self):		
		
		while True:
			fdr = []
			fdr.append(self.sockserver)
			for  s in self.cltsocks:
				fdr.append(s)
			#self.mtxsocks.release()
			infds =[]
			for fd in fdr:
				try:
					r,w,e = select.select([fd],[],[],0.00001)
					if r:
						infds+=r
				except:
					self.app.getLog().error(traceback.format_exc())
					self.app.getLog().error('current fd:'+str(fd))
					self.cltsocks.remove(fd)
					fd.close()
				
			'''
			try:
				infds,w,e = select.select(fdr,[],fdr,1)
				if e:
					self.app.getLog().error('select errors:'+str(e))
					break
			except:
				traceback.print_exc()
				self.app.getLog().error(traceback.format_exc())
				self.app.getLog().error('select exception:'+str(fdr))
				break
			'''
			if infds==[]:# timeout
				continue
			for s in infds:
				if s == self.sockserver: #新连接到达 
					sock,peer = self.sockserver.accept()
					self.app.getLog().debug('new client come in:'+str(peer)+str(sock))					
					
					e = DeviceEvent_Base()
					e.type = DeviceEvent_Base.INCOMMING_CONNECTED
					e.conn = self.connCLS(self)
					e.conn.codec = self.codecCLS(self)
					e.conn.codec.conn = e.conn
					e.conn.sock = sock
					
					sock.delta[sock.fileno()] = e.conn #socket 绑定连接对象
					
					self.event(e) #通知外部对象，ActiveObjectMgr必须匹配到对应的设备
					if e.accept == False: #应用拒绝连接
						sock.close()							
					else: #单线程，无需数据保护
						self.cltsocks.append(sock) #此刻未进行aobject与sock的关联
						
					continue
				else: #客户套接字产生数据
					#print s.conmgr
					conn = None
					error = False
					try:
						conn = s.delta[s.fileno()]
						d = s.recv(1024)
						#print len(d),d
						if not d: # remote shudown
							error = True
					except: # socket connection lost
						traceback.print_exc()
						error = True
					if  error:
						e = DeviceEvent_Base()
						e.type = DeviceEvent_Base.DISCONNECTED
						e.conn = conn
						self.event(e)
						s.delta.pop(s.fileno())
						self.app.getLog().error('client disconnect:'+str(s)+str(self.cltsocks))
						self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
						self.app.getLog().error(str(self.cltsocks))
						self.app.getLog().error( '-------')
						conn.close()
						print 'socket lost..'
						continue
					
					r = False
					try:
					
						r = conn.codec.queueIn(d,conn) #数据入队列
					except:
						print type(conn),dir(conn)
						traceback.print_exc()
						
					if not r:
						self.cltsocks.remove(s)  #连接断开也可以即可通知ActiveObject
						conn.close()
						continue
					self.exc_mq.queueIn(conn)

	
	
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
		self.mtxsvc = threading.Lock()

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
	

					
	