# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

import message
from message import *
import network
from network import * 
from msg_imgput import * 

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
Error_FileServer_Base = 2000
EFSB = Error_FileServer_Base
Error_FileWrite_Exception = EFSB+1
Error_FileCreate_Failed = EFSB+2
Error_FileOpen_Failed = EFSB+3 
Error_FilePut_Timeout = EFSB+4
Error_FilePut_Reject = EFSB+5
Error_FileRead_Failed = EFSB+6

class FileServer(NetService):
	def __init__(self,name):
		NetService.__init__(self,name)
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
		if msg== 'imageput_init':
			file = m.attrs
			file['delta'] = None
			file['conn'] = conn
			conn.delta = file
			r = self.eventFileRequest(file)
			
			return 
		
		if msg == 'imageput_data':
			self.eventFileData(conn.delta,m.bin)
			return 
		
		if msg == 'imageput_end':
			self.eventFileFinished(conn.delta,m.bin)
			return
		
		
		
	def eventGotMessage(self,msglist,conn):
		for m in msglist:
			self.dispatchMsg(m)
			
	def eventFileGetRequest(self,file):
		''' 客户主动到服务器拉文件
		Get请求到达，通过之后便启动Thread来单独发送一个文件			
		'''
		pass
		
	def eventFileGetData(self,file,d):
		pass
		
	def eventFileGetFinished(self,file):
		'''完成get 文件的工作
		'''
		pass
		
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
		filename = self.getFilePutName(file)
		try:
			fd = open(filename,'wb')
			file['fd'] = fd
			file['conn'].sendMessage(MsgCallReturn())
		except:
			m = MsgCallReturn(False,Error_FileCreate_Failed,u'File Creating Exception occurred!')
			file['conn'].sendMessage(m)
			file['conn'].close()
	
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
		
	def getFilePutName(self,file): # should be overrided
		return file['filename']
	

class FileClient:
	def __init__(self,indicator=None):
		self.recvmsg=[] #接收到的消息
		self.mtx_recvmsg=threading.Condition()
	
	def startPut(self,filename,addr,indicator=None):
		'''
			file - string {'delta':None,'conn':conn,'filename','modifytime','filesize','digest','fd','sentbytes'}   
			sentbytes - 已发送字节
		'''
		conn = NetConnection(recvfunc = self.recvEvent)
		r = conn.connect( addr)
		if r == False:
			return NETMSG_ERROR_DESTHOST_UNREACHABLE
			
		m = MsgImagePut_Init()
		file = m.attrs
		file['filename'] = filename
		file['conn']=conn
		fd = None
		try:
			file['modifytime'] = utils.getmtime(file)
			file['filesize'] =  os.path.getsize(file)
			file['digest'] = utils.getfiledigest(file)
			file['sentbytes'] = 0
			fd = open(file,'rb')
		except:
			conn.close()
			return Error_FileOpen_Failed
		file['fd'] = fd
		conn.delta = file
		self.beforePut_Init(file)
		r = conn.sendMessage(m)
		if not r:
			conn.close()
			return NETMSG_ERROR_CONNECTION_LOST
			
		thread = NetConnThread(conn)
		m = self.getMessageTimeout()
		if not m: #超时没有返回，错误处理
			conn.close()
			return Error_FilePut_Timeout #超时
		if m.getMsg()!='callret':
			conn.close()
			return Error_FilePut_Reject
		if m.attrs['succ'] != True:
			conn.close()
			return Error_FilePut_Reject
		# file put request ok?!  next....
		# 开始读文件 
			
		while True:
			d = fd.read(1024*50)
			if not d: break
			m = MsgImagePut_Data(d)
			r = conn.sendMessage(m)
			file['sentbytes']+=len(d)
			if indicator:
				indicator(file) #提示发送进度
			if not r: 
				conn.close()
				return NETMSG_ERROR_SENDDATA_FAILED
			
		m = MsgImagePut_End()
		r = conn.sendMessage(m)
		if not r: 
			conn.close()
			return NETMSG_ERROR_SENDDATA_FAILED
		conn.close()
		return ERROR_SUCC
		
		#1.发送put_init
	def getMessage(self,lock=False):
		m = None
		if lock:self.mtx_recvmsg.acquire()
		
		if len(self.recvmsg):
			m = self.recvmsg[0]
			del self.recvmsg[0]
		if lock:self.mtx_recvmsg.release()
		
		return m
	
	def getMessageTimeout(self,timeout = 5):
		#等待第一个包返回 
		self.mtx_recvmsg.acquire()
		m = self.getMessage()
		if not m:
			self.mtx_recv.wait(timeout) #等待5秒钟如果没有返回则
		m = self.getMessage()
		self.mtx_recvmsg.release()
		return m
	
	
	def beforePut_Init(self,file):
		''' should be overrided
			file - {}
		'''
		pass
		
	def dispatchMsg(self,m,conn):
		file = conn.delta
		self.mtx_recvmsg.acquire()
		self.recvmsg.append((m,conn))
		self.mtx_recvmsg.notify()
		mtx_recvmsg.release()
	
	def recvEvent(self,evt):		
		if evt.type == NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				self.dispatchMsg(m,evt.conn)
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			print 'connection lost!'
	
if __name__=='__main__':
	pass
	