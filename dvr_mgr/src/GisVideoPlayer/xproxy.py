# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading
import select
import utils
from network import *
from plugin_service import PluginPacketQueue
'''
模拟本地mapshow直连到Imageplay.PluginService端口
连接到xbridge的12788端口
发送 {id,type}
id = time.time()
type = 'imageplay'

jason格式 编码


imageplay在本地，定是能连接上
主要处理与xbridge的连接

XProxy可以单独进程运行，也可以被集成进Imageplay进程
xproxy作为pluginservice的向外连接模块，连接到xbridge
'''


class XProxy:
	def __init__(self,owner,server=('sw2us.com',12788)):
		self.sock1 = None
		self.sock2 = None
		self.server = server
		self.svc = owner
		self.sessionid='11223344'
		self.exiting = False
		self.conn = None #与xbridge的连接
		
		
	def getSessionId(self,renew=False):
		
		if renew:
			self.sessionid = str( int(time.time()) )
			
		return self.sessionid
	
	
	
	def getConnection(self):
		return self.conn
	
	def start(self):
		##self.sock1 = socket.socket()
		##self.sock1.connect(self.pluginsvc)
		self.thread = threading.Thread(target=self.threadRecv)
		self.thread.start()
		debug = self.svc.app.getConf().get('xproxy.debug')
		self.getSessionId(not debug)
		
		return True
	
	def stop(self):
		try:
			self.exiting = True
			#self.sock1.close()
			#self.sock2.close()
		except:
			traceback.print_exc()
		self.thread.join()
		
	def doConnectXBridge(self):
		print 'try to connect xbridge...'
		#debug为true表示开发状态，session值固定的11223344,如果为false，
		#将自动产生sessionid，浏览器动态获取sessionid，通过xbridge转发
		
		m = {'id':self.getSessionId(),'type':'imageplay'}
		print m
		conn = NetConnection(recvfunc = self.recvEvent,
							 queuecls=PluginPacketQueue)
		r = conn.connect(self.server)
		if not r: return False
		print 'connected to xbridge!'
		thread = NetConnThread(conn)
		self.conn = conn
		d = json.dumps(m)
		self.conn.sendData(d) #发送连接标志
		#time.sleep(4)
		#self.conn.sendData('aaaa'*10)
		return True
		
	def recvEvent(self,evt):
		if evt.type == NetConnectionEvent.EVENT_DATA:
			msglist = evt.data
			for m in msglist:
				self.svc.dispatch(m,evt.conn)
			
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			self.conn = None
			print 'connection lost!'

	def threadRecv(self):
		print 'service threading entering...'
		while not self.exiting:
			if self.conn == None:
				if self.doConnectXBridge() == False:
					time.sleep(5)
					continue
			time.sleep(5)
			
				
		print 'MainThread Exiting...'
	
if __name__=='__main__':
	XProxy().start()
	utils.waitForShutdown()