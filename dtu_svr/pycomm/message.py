# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

'''
------------------
msghdr
cmdtxt
\0\0
二进制流
-----------------
视频包由三部分构成: MetaMessage数据元封套,控制命令文本(json格式),二进制数据，后两者之间采用连续两个\0区分，表示开始二进制流数据
[metamsg,cmdtxt,bindata]
bindata部分格式、编码由cmdtxt控制

# [magic,size,compress,encrypt,version],[command text(json)],[\0\0],[binary data..]
'''

COMPRESS_NONE = 0
COMPRESS_ZLIB = 1
COMPRESS_BZIP2 = 2

ENCRYPT_NONE = 0
ENCRYPT_MD5  = 1
ENCRYPT_DES  = 2


class MessageBase:
	def __init__(self,type='',bin=None):
		#self.type = type
		self.attrs={'msg':type}
		self.bin = bin
	
	def __setitem__(self,key,value):
		self.attrs[key] = value
		
	def __getitem__(self,key):
		return self.attrs.get(key)
	
	def getMsg(self):
		return self.getValue('msg')
		
	def getValue(self,key):
		if self.attrs.has_key(key):
			return self.attrs[key]
		return None
	
	def getBinary(self):
		return self.bin
		
	def marshall(self):
		
		d = json.dumps(self.attrs)
		if self.bin:
			d+='\0\0'+ self.bin
		return d
	
	@classmethod
	def unmarshall(cls,d):
		m = None		
		sep = d.find('\0\0')
		txt = None
		bin = None
		if sep == -1:
			txt = d
		else:
			txt = d[:sep]
			bin = d[sep+2:]		
		m = MessageBase()
		try:
			m.attrs = json.loads(txt)
			if type(m.attrs) != type({}):
				return None			
			m.bin = bin
		except:
			m = None
		return m
	
	def __str__(self):
		return str(self.attrs)
		
class MsgCallReturn(MessageBase):
	def __init__(self,succ=True,errno=0 ,errmsg='',value=None,bin=None):
		MessageBase.__init__(self,'callret',bin)
		self.attrs['succ']=succ
		self.attrs['errno']=errno
		self.attrs['errmsg']=errmsg
		self.attrs['value']=value
		
class NetMetaPacket:
	# [magic,size,compress,encrypt,version],[command text(json)],[\0\0],[binary data..]
	def __init__(self,msg=None,compress=COMPRESS_NONE,encrypt = ENCRYPT_NONE ):
		self.msg = msg
		self.size4 = 0
		self.compress1 = compress
		self.encrypt1 = encrypt
		self.ver4 = 0x01000000 # means 1.0.0.0
	magic4=0xEFD2BB99
	
	@classmethod
	def minSize(cls):
		return 14
		
	def marshall(self):
		d = self.msg.marshall()
		if self.compress1 == COMPRESS_ZLIB:
			d = zlib.compress(d)
		else:
			self.compress1 = COMPRESS_NONE
		self.encrypt1 = ENCRYPT_NONE 
		# [magic,size,compress,encrypt,version],[command text(json)],[\0\0],[binary data..]
		r = struct.pack('!BBI',self.compress1,self.encrypt1,self.ver4)
		r+= d
		self.size4 = len(r)+4
		r = struct.pack('!II', self.magic4,self.size4) + r
		# size =包含自身变量的整个包大小
		return r

'''
simplemessage
不携带二进制数据流，简化消息包头格式,仅仅带有4字节的大小描述
simpleMessage与unmarshall配合使用, flex代码目前采用SimpleMessage+NetSimplePacket编码
[size(4),content(zlib+json)]
'''
class SimpleMessage(MessageBase):
	def __init__(self,type=''):
		MessageBase.__init__(self,type)
		
	def marshall(self):
		d = json.dumps(self.attrs)		
		return d	

	@classmethod
	def unmarshall(cls,d):
		#print 'unmarshall:',d
		txt = d		
		m = MessageBase()
		try:
			m.attrs = json.loads(txt)
			if type(m.attrs) != type({}):
				return None						
		except:
			m = None
		#print 'SimpleMessage.unmarshall ok:',m.attrs,type(m)
		return m


class NetSimplePacket:
	# [size,cotent(zlib+json)]
	def __init__(self,msg=None,compress=COMPRESS_NONE,encrypt = ENCRYPT_NONE ):
		self.msg = msg
		self.size4 = 0
		self.compress1 = compress
		self.encrypt1 = encrypt
	
	def marshall(self):
		d = self.msg.marshall()
		d = zlib.compress(d)
		d= struct.pack('!I',len(d))+d		
		return d


Error_Base = 1000
Error_SpaceNotEnough = Error_Base + 1	
	
errors={
	Error_SpaceNotEnough:u'存储空间不够',
}
		
		
if __name__=='__main__':
	
	#print NetMetaPacket(msg=MsgCallReturn(value=range(10),bin='abc' ),compress=COMPRESS_NONE).marshall()
	#print NetMetaPacket.minSize()
	m = MsgCallReturn()
	m['name']='scott'
	print m.attrs
	