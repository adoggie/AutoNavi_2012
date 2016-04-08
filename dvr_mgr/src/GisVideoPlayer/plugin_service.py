# -- coding:utf-8 --
# network.py 
# bin.zhang@sw2us.com 
# 2012.3.8
# revision:  
#

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import select,struct,zlib

import message
from message import * 
from errbase import *
from network import *
from msg_plugin import * 

		
#NetPacketQueue 处理消息分解
class PluginPacketQueue(NetPacketQueue):
	def __init__(self,app,conn = None,size= 1024):
		NetPacketQueue.__init__(self,conn,size)
		self.app = app #实例程序
		
	'''
		@return: (false,errcode) - 脏数据产生
		消息包格式: size(4)+content(any)
		每个包以json编码,头部4字节表示内容长度,big endian
	'''
	def dataQueueIn(self,d):
		#print 'PluginPacketQueue in:',d
		rc = (True,2)
		self.bf+=d
		d = self.bf
		while True:			
			
			if len(d)< 4:
				rc = True,0 #数据不够,等待
				break
			size, = struct.unpack('!I',d[:4])
			print size,d
			if len(d) < size+4: #数据不够
				rc = True,1
				break
			s = d[4:size+4]
			d = d[size+4:]
			#print size,len(s)
			#s = zlib.decompress(s)
			m = MsgPlugin_Base.unmarshall(s)
			if m == None:
				return False,NETMSG_ERROR_MESSAGEUNMARSHALL
			self.mtxptks.acquire()
			self.pktlist.append(m)
			self.mtxptks.notify()			
			self.mtxptks.release()
		self.bf = d
		return rc
	

class PluginService(NetService):
	def __init__(self,app,name,addr,queuecls = PluginPacketQueue):
		NetService.__init__(self,name,addr,queuecls)
		self.clientconn = None
		self.app = app
		self.proxy = None
		
		
	def getProxy(self):
		return self.proxy
	
	def eventConnCreated(self,conn):
		try:			
			NetService.eventConnCreated(self,conn)
			thread = NetConnThread(conn)
			if self.clientconn:
				self.clientconn.close()
			self.clientconn = conn
			print 'new plugin client coming..'
		except:
			traceback.print_exc()
	
	def eventConnDisconnected(self,conn):		
		NetService.eventConnDisconnected(self,conn)
		print 'plugin client exit....'
		
	def eventGotMessage(self,msglist,conn):
		for m in msglist:
			self.dispatch(m,conn)
			
	def dispatch(self,m,conn):
		#print type(m)
		msg = m.getMsg()
		print msg
		if msg == 'plugin_geosightchanged_1':
			self.plugin_GeoSightChanged(m)
			return
		if msg =='plugin_maproadselected_1':
			return
		
		if msg == 'plugin_imagepathselected_1':
			self.plugin_ImagePathSelected(m)
	
		
	#overrided NetService.start()	
	def start(self,enableproxy=False):
		from xproxy import XProxy
		r = NetService.start(self)	#启动监听服务
		if not r: return False
		if enableproxy:	#启动socket转发代理
			self.proxy = XProxy(self)
			r = self.proxy.start()
		return True
	
		
	def sendMessage(self,m):
		import zlib
		try:
			#print 'pluginsvc sendMessage:',m.getMsg()
			d = m.marshall()
			#d = zlib.compress(d)
			d=struct.pack('!I',len(d))+d
			conn = self.clientconn
			if self.proxy:
				#print 'proxy.conn:',self.proxy.conn
				conn = self.proxy.conn
			#print 'd:',len(d)
			
			conn.sendData(d)
		except:
			#self.clientconn = None
			pass
#			traceback.print_exc()
	
	#地理可视界改变
	def plugin_GeoSightChanged(self,m):
		
		rect = m.attrs['rect']
		print rect
		self.app.getQueryWnd().OnGeoSightChanged(rect)
	
	def plugin_ImagePathSelected(self,m):
		self.app.getQueryWnd().OnMapImagePathSelected(m)
	

	
if __name__=='__main__':
	pass