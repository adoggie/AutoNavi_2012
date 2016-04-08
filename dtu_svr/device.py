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
		#�����ǻ�õ�module id,subclass����֧��
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
	#�豸���ӵ�ַ������Ϣ
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
		self.handle = None #ͨ�ž��
		
	def write(self,bytes):
		try:
			self.handle.sendall(bytes)
		except:
			traceback.print_exc()
	
	def read(self):
		#ĳЩ�������������ֱ�Ӷ�ȡ 
		pass
	
	def setCodec(self,codec):
		self.codec = codec

#�����豸�¼�����
class DeviceEvent_Base:
	CONNECTED = 1
	DISCONNECTED = 2
	RECVED_DATA = 3
	SENT_DATA = 4
	INCOMMING_CONNECTED = 5
	UNDEFINED = 0xff
	def __init__(self):
		self.data = None #�����¼��������� ActiveObject_Data
		self.type = DeviceEvent_Base.UNDEFINED
		#self.source = None #�¼�Դ����
		self.conn = None #�豸���Ӷ���,tcp socket
		self.accept = True
		
#�¼����ն���	
class DeviceEvent_Sink:
	
	def __init__(self):
		pass
	
	def event(self,e):
		#�����������ӣ����������ý���������
		#if e.type == INCOMMING_CONNECTED:
		#	if isinstance(e.conn,DeviceConnection_Tcp):
		#		
		pass

#�����ػ�,�ṩĳ��ͨ�����ӵķ���
#���ݵ��ｫ������Ϣ��������	
class DaemonService_Base:
	
	def __init__(self):		
		pass
	
	def newline(self,url,codec=MediaCodec_Null,async= False):
		pass
		
class DaemonService_Tcp(DaemonService_Base,threading):
	#���ӽ��뽫�Զ�����DeviceConnection_Tcp���󣬲��� DeviceData_Event���ݸ�������(sink),sink�������ö�Ӧ�Ľ�����
	#
	def __init__(self,addr,sink,connCLS=DeviceConnection_Base,codecCLS=MediaCodec_Null):
		#@param addr - (host,port)
		#@param sink - ��Ϣ���ն���DeviceEvent_Sink������
		#@param connCLS - ������ DeviceConnection_Tcp������
		DaemonService_Base.__init__(self)
		threading.__init__(self)
		self.connCLS = connCLS
		self.codecCLS = codecCLS
		self.sink = sink
		self.addr = addr
		self.cltsocks=[]
		self.lockClientsocks= threading.Lock()
		
		self.initNetwork()
	
	#tcp�������� ��ʼ��
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
					if s == self.sockserver:	#�����ӽ���
						sock,peer = self.sockserver.accept()
						e = DeviceEvent_Base()
						e.type = DeviceEvent_Base.INCOMMING_CONNECTED
						e.conn = self.connCLS(self) #����һ�����Ӷ��� DeviceConnection_Base
						e.conn.codec = self.codecCLS()	#���ý�����
						e.conn.handle = sock
						sock.conn = e.conn 		#socket ����Ķ�̬���ԣ����ڿ��ٶ�λ��������
						self.sink.event(e) 		#֪ͨ�ⲿ����  Ĭ�� ActiveObject_Manager����ȷ��
						if e.accept == False: 	#ActiveObject_ManagerӦ�þܾ�����
							sock.close()							
						else:
							self.cltsocks.append(sock) #�˿�δ����aobject��sock�Ĺ��� ��ӵ� fd_set
						continue
					else:
						try:
							d = s.read(1024)
							if not d:	# null ��ʾ�Է�����ر���
								raise 'error'
						except: # socket connection lost
							self.lockClientsocks.acquire()
							self.cltsocks.remove(s)  #���ӶϿ�Ҳ���Լ���֪ͨActiveObject
							self.lockClientsocks.release()
							continue
						
						#��������sock�󶨵�DeviceConnection_Base�Ľ�����
						d,retry = s.conn.codec.decode(d) #���������������� ActiveObject_ModuleData
						if d:	#�����ݰ��������
							if s.conn.aom:	#�Ѿ���������aom������						
								s.conn.aom.ao.readData(d,s.conn) # ����·���� ���䵽ActiveObject����������ɸ���ͬ��module
							else:#δ����������Ҫ����������䵽ActiveObject_Manager
								e = DeviceEvent_Base()
								e.type = DeviceEvent_Base.RECVED_DATA
								e.conn = s.conn
								e.data = d		#�����Ϣ����
								self.sink.event(e) #��ActiveObject_Managerȥ��������������Ϣ��
								if e.accept == False: #����ʧ�ܣ��ر�socket
									self.lockClientsocks.acquire()
									self.cltsocks.remove(s)  
									self.lockClientsocks.release()
									continue						
						else: #���������Ƿ������Ч����Ӧ�þ��綪��
							if retry == False: #������Ч��
								self.lockClientsocks.acquire()
								s.close()
								self.cltsocks.remove(s)  #���ӶϿ�Ҳ���Լ���֪ͨActiveObject
								self.lockClientsocks.release()
								continue
							
							
		except:
			traceback.print_exc()
		pass
	
	
	def newline(self,module,url):
		#�������⽨��tcp����
		#@param module  MediaDataType.* ͨ��ý������
		#@param codec ������ Ĭ�ϵĽ����������������κδ���
		#@param async �Ƿ����첽����ģʽ,ͬ����ʽ�������û����������Ӷ����ϵ���read()
		#��ͬ��url ������ͬ��connection����
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
#ͨ�Ų����������ӳ���
PORTMAP=[
	{'name':'com1','proto':'serial','port':'COM1','host':'','codec':MediaCodec_SerialComm_Gps,'devicetype':'wait for...'},
	]	

###################################33

#class ActiveObject_ModuleData:
#	def __init__(self):		
#		self.data = None 	#
#		self.module = None 	#ͨ������

class ActiveObject_Module:
	def __init__(self,parent,type,name=''):
		self.ao = parent
		self.name = name
		self.type  = MediaDataType.UNDEFINED
		self.dataqueue=[] 		#��ActiveObject_Data
		self.conn = None	#���Ӷ���
		self.id = '' 	#ģ������Ӳ����ʾ
		self.url = None #������Ϣ
		
	def connect(self):
		#������������
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
	
#active object�Ǹ�Ӧ�ø����ϵ��豸�������й�������������˶��������
#���յ������ݣ��ȴ�����ϵͳ���ʡ���ˢ; ���ڶ�ʵʱ��Ҫ��Ƚϸߵ������
#ActiveObjectҪ�����ύ���ݵ���������ϵͳȥ 
class ActiveObject_Base:
	#ϵͳ����
	def __init__(self,owner):
		#codecCLS ���������
		self.owner = owner
		self.modules = {} #ͨ������
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
		#@param: data -  �����Ϣ��
		#@return True - ����ƥ�䵽�����module�豸.else False
		r = False
		for m in self.modules:
			if m.readData(data,conn):	#����ֻҪ�ǹ����κ�һ��module�ľ�okay
				r = True				
		return r

class ActiveObject_Manager(DeviceEvent_Sink):
	def __init__(self,deliverNext):
		self.lockPendingConns = threading.Lock()
		
		sef.pendingConns=[] #δ��ȷ�Ķ���
		self.objects=[]	#ao list
		self.lockObjects = threading.Lock()
		
	def event(self,e):
		if e.type == DeviceEvent_Base.INCOMMING_CONNECTED:
			#Ŀ���ַ��֤
			self.lockPendingConns.acquire()
			self.pendingConns.append(e.conn)
			self.lockPendingConns.release()
			
		elif e.type == DeviceEvent_Base.RECVED_DATA:
			self.lockObjects.acquire()
			for o in self.objects:
				# e.data ��������������Ϣ��
				if o.readData(e.data,e.conn):#������AcitiveObject�������ˣ�֮������ݽ��� ��ֱ�Ӵ��ݵ�ActiveObject.readData()					
					break
				else:
					e.accept = False #�޷�ƥ���Ӧ�Ķ���				
			self.lockObjects.release()
			#
			self.lockPendingConns.acquire()
			self.pendingConns.remove(e.conn) #��pending����ȥ��
			self.lockPendingConns.release()
			
#class DtuServer:
#	def __init__(self):		
#		setattr(socket.socket,'conn',None) #Ӧ������
#
#
#if __name__=='__main__':
#	server = DtuServer()
	
					
	