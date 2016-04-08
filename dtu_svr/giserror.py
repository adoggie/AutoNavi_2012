# -*- coding:utf-8 -*-

# revisions:

import sys,os
sys.path.insert(0,'C:/Ice-3.3.1-VC90/bin')
sys.path.insert(0,'C:/Ice-3.3.1-VC90/python')

import traceback,threading,time,struct,os,os.path,datetime
import datacache,dgw
from appconfig import SimpleConfig

import Ice
Ice.loadSlice('-I./idl idl/gis.ice')
from newgis  import *

##############################################################
appconf = SimpleConfig()		
appconf.load('ctrlserver.txt')
##############################################################
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'	#self.config.getValue('django_module')
sys.path.insert(0,appconf.getValue('django_module_path'))
from giscore.models import *
##############################################################
VERSION=''


class CtrlServer(ICtrlServer):
	def __init__(self,app):
		self.app = app
		self.init()
		
	def invokeOneway(self, value, stream, current=None):
		pass
	
	def getSequence(self, current=None):
		self._seqno+=1
		return self._seqno
	
	def getType(self, current=None):
		return 'GRT_UPDATER'
	
	def getId(self, current=None):
		return '' #self._app.getPropertyValue('server.id')
	
	def getTimestamp(self, current=None):
		return int(time.time())
	
	def getVersion(self,current=None):
		return VERSION

	#das 传送ao 数据进入	
	def updateAoData(self,aoid,jsondata,c=None):
		self.cachedserver.pushData(aoid,jsondata)
	
	#dwg服务ice接口注册进入
	def addDGW(self,dgw,c=None):
		pass
	
	#keepalive(string sid,string type,string commstr)
	def registerModule(self,sid,type,commstr,c=None):
		try:
			#print 'registerModule:',sid,type,commstr
			m = None
			cnt = SysModule.objects.filter(sid=sid.strip()).count()			
			if cnt == 0:
				m = SysModule()
				m.sid = sid.strip()
			else:
				m = SysModule.objects.get(sid=sid.strip())
			m.type = type
			m.uptime = datetime.datetime.now()
			m.commstr = commstr
			m.save()
		except:
			traceback.print_exc()
	
	def keepalive(self,sid,c=None):
		try:
			m = SysModule.objects.get(sid=sid.strip())
			m.uptime = datetime.datetime.now()
			m.save()
		except:
			traceback.print_exc()
		
#--------------
	def init(self):
		self.cachedserver = datacache.CachedServer()
		self.dgw = dgw.DataGateway()
		self.cachedserver.attachClient(self.dgw) # dgw and cachedserver binding
	
	def mainloop(self):
		interval = int(appconf.getValue('sync_interval'))
		while True:						
			time.sleep( interval ) #
#############################################
#################################################

class App(Ice.Application):
	def	__init__(self):		
		pass
	
	def test(self):
		#self.service.killProcess(2968)
		pass
	
	def run(self, args):
		self.service = CtrlServer(self)
		self._adapter = self.communicator().createObjectAdapter("CtrlServerAdapter")
		self._adapter.add( self.service, self.communicator().stringToIdentity('ctrlserver')) #服务入口接口对象 
		self._adapter.activate()
		#self._log.debug( 'endpoint (%s) service start!'%VERSION)
		print 'ctrlserver started!'
		self.communicator().waitForShutdown()
		return 0

##############################################################

if __name__=='__main__':
	server = App()
	sys.exit(server.main(sys.argv, "ctrlserver.txt"))
	
	
		
	