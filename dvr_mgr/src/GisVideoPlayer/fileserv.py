# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading

import message
from message import *
import network
from network import * 
from msg_imgput import * 
from errbase import *
import utils

'''
FileServer 定时删除 未成功传输的文件(依据文件名称) 
文件传输结束，及时从临时目录搬走文件

重建idx: 到影像目录下找到 dat,mov文件，生成trp和 .des文件 ，des文件为json格式，记录此影像是否被索引成功，以及影像其他的数据
trp文件采用trpmapfix产生路段匹配文件 .road ,里面包含了所有影像走过的路段信息
所以一个影像必须具备 .trp,.des,.road,.mov四个文件
.des .trp .road 可以在客户端直接转换好，将这些文件通过一次image_put上传到服务器

服务器在每个zone都设置一个tempdir目录，接收文件之后直接更名文件到正确的存储位置，免去了不同zone拷贝的开销
'''

class FileServer(NetService):
	def __init__(self,name,addr):
		NetService.__init__(self,name,addr)
		self.tmpdir='.'
		self.conf = None
		
	
	def init(self,conf): # conf - json
		pass
		
	def setTempFileDir(self,path):
		'''设置临时文件存放目录'''
		pass
		
	def run(self,wait=False):
		pass
		
	def shutdown(self):
		pass
	
	def dispatchMsg(self,m,conn):
		msg = m.getMsg()
		#print msg
		if msg== 'imageput_init':
			file = m.attrs
			file['delta'] = None
			file['conn'] = conn
			conn.delta = file
			r = self.eventFilePutRequest(file)
			return 
		
		if msg == 'imageput_data':
			file = conn.delta
			self.eventFilePutData(file,m.bin)
			return
		
		if msg == 'imageput_end':
			self.eventFilePutFinished(conn.delta)
			return
		
		
		
	def eventGotMessage(self,msglist,conn):
		for m in msglist:
			self.dispatchMsg(m,conn)
			
	#def eventFileGetRequest(self,file):
	#	''' 客户主动到服务器拉文件
	#	Get请求到达，通过之后便启动Thread来单独发送一个文件			
	#	'''
	#	pass
	#	
	#def eventFileGetData(self,file,d):
	#	pass
	#	
	#def eventFileGetFinished(self,file):
	#	'''完成get 文件的工作
	#	'''
	#	pass
		
	def eventFilePutRequest(self,file):
		''' 文件请求到达  
			file - {'delta':None,'conn':conn,'filename','modifytime','filesize','digest','fd'}   
				利用file可设置delta用于控制上下文, conn 表示连接对象
				fd - 打开文件读写句柄
			@return :  
				MsgCallReturn(True) 如果统一接收则返回MsgCallReturn(True)或者返回True
				拒绝则返回MsgCallReturn(False,...)
		'''
		#1.检查存储空间是否到lowater		
		pass

	
	def eventFilePutData(self,file,d):
		try:
			fd = file['fd']
			fd.write(d)
			fd.flush()
		except:
			m = MsgCallReturn(False,Error_FileWrite_Exception,u'File Writing Exception occurred!')
			file['conn'].sendMessage(m)
			file['conn'].close()
		
	
	def eventFilePutFinished(self,file):
		conn = file['conn']
		fd = file['fd']
		fd.close()
		#回写一个ok
		conn.sendMessage(MsgCallReturn())
		time.sleep(2)

	
	def eventConnCreated(self,conn):
		NetService.eventConnCreated(self,conn)
		thread = NetConnThread(conn)
		
	
	def eventConnDisconnected(self,conn):
		NetService.eventConnDisconnected(self,conn)
		if not conn.delta:return 
		file = conn.delta
		try:
			#中断，必须删除临时文件
			file['fd'].close()
			os.remove( file['filename'])
		except:
			pass

class FileClient:
	def __init__(self,indicator=None):
		self.recvmsg=[] #接收到的消息
		self.mtx_recvmsg=threading.Condition()
		self.wait = utils.MutexObject()
	
	def startPut(self,filename,addr,indicator=None):
		'''
			file - string {'delta':None,'conn':conn,'filename','modifytime','filesize','digest','fd','sentbytes'}   
			sentbytes - 已发送字节
		'''
		
		print 'start put:',filename
		
		file = {} #m.attrs
		file['filename'] = filename
		
		fd = None
		try:
			file['modifytime'] = utils.getmtime(filename)
			
			file['filesize'] =  os.path.getsize(filename)
			file['filesize_bytes'] = file['filesize']
			#file['digest'] = utils.getfiledigest(file)
			file['sentbytes'] = 0
			fd = open(file['filename'],'rb')
		except:
			traceback.print_exc()
			return Error_FileOpen_Failed
		file['fd'] = fd		
		r = self.beforePut_Init(file)
		if not r:
			fd.close()
			return Error_FileOpen_Failed
		
		#conn = NetConnection(recvfunc = self.recvEvent)
		conn = NetConnection()
		r = conn.connect( addr)
		if r == False:
			return NETMSG_ERROR_DESTHOST_UNREACHABLE
		file['conn']=conn
		conn.delta = file
		m = MsgImagePut_Init(file['filename'],file['modifytime'],file['filesize'],file.get('digest','') )
		m.attrs['dat'] = file.get('dat','')
		m.attrs['trp'] = file.get('trp','')
		
		r = conn.sendMessage(m)
		file['filesize'] = file['filesize_bytes']
		
		if not r:
			conn.close()
			return NETMSG_ERROR_CONNECTION_LOST
		
		thread = NetConnThread(conn)
		
		m = conn.getQueue().getMessage(5)
		
		if not m: #超时没有返回，错误处理
			print 'server timeout..'			
			conn.close()
			return Error_FilePut_Timeout #超时
		if m.getMsg()!='callret':
			conn.close()
			return Error_FilePut_Reject
		if m.attrs['succ'] != True:
			conn.close()
			print m.attrs
			return Error_FilePut_Reject
		# file put request ok?!  next....
		# 开始读文件 
		while True:
			d = fd.read(1024*150)
			if not d: break
			m = MsgImagePut_Data(d)
			r = conn.sendMessage(m)
			file['sentbytes']+=len(d)
			if indicator:
				indicator(file) #提示发送进度
			if not r:
				self.abortPut(file)
				conn.close()
				return NETMSG_ERROR_SENDDATA_FAILED
			#time.sleep(5)
			
		m = MsgImagePut_End()
		r = conn.sendMessage(m)
		if not r:
			self.abortPut(file)
			conn.close()
			return NETMSG_ERROR_SENDDATA_FAILED
		self.afterPut_Done(file)
		conn.close()
		thread.join()
		return ERROR_SUCC
		
		#1.发送put_init
	#def getMessage(self,lock=False):
	#	m = None
	#	if lock:self.mtx_recvmsg.acquire()
	#	
	#	if len(self.recvmsg):
	#		m = self.recvmsg[0]
	#		del self.recvmsg[0]
	#	if lock:self.mtx_recvmsg.release()
	#	
	#	return m
	#
	#def getMessageTimeout(self,timeout = 5):
	#	#等待第一个包返回 
	#	self.mtx_recvmsg.acquire()
	#	m = self.getMessage()
	#	if not m:
	#		self.mtx_recv.wait(timeout) #等待5秒钟如果没有返回则
	#	m = self.getMessage()
	#	self.mtx_recvmsg.release()
	#	return m
	
	
	def beforePut_Init(self,file):
		''' should be overrided
			这里在文件头塞入其他信息，例如dat文件数据
			file - {}
		'''
		pass

	def afterPut_Done(self,file):
		pass

	def abortPut(self,file):
		pass

		
	#def dispatchMsg(self,m,conn):
	#	file = conn.delta
	#	self.mtx_recvmsg.acquire()
	#	self.recvmsg.append((m,conn))
	#	self.mtx_recvmsg.notify()
	#	self.mtx_recvmsg.release()
	#
	#def recvEvent(self,evt):		
	#	if evt.type == NetConnectionEvent.EVENT_DATA:
	#		for m in evt.data:
	#			self.dispatchMsg(m,evt.conn)
	#	if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
	#		print 'connection lost!'
	
if __name__=='__main__':
	pass
	