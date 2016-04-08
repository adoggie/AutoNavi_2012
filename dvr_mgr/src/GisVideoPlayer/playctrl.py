# -*- coding: utf-8 -*-

#playctrl.py
#播放控制

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading
import ffmpeg

from mediasvr import *

from playconsole import *
from playquery import *

from plugin_service import *
import utils



class ImagePlayApp:    
	def __init__(self, *args):
		ffmpeg.InitLib()				
		self.svcplugin = None	
		self.conf = None
		self.conf = utils.loadjson('plugin.txt')
		self.wndconsole = PlayConsoleWindow(self)		
		self.wndquery = PlayQueryWindow(self)
		
	def __del__(self):
		pass    
	
	
	def showGeoPosition(self,pt): #反射到内业软件
		'''
			pt - {'lon','lat','time','speed','angle']}
			
		'''
		pass
	
	def getConsoleWnd(self):
		return self.wndconsole
	
	def getQueryWnd(self):
		return self.wndquery
	
	def getPluginService(self):
		return self.svcplugin
	
	def main(self):
		'''
			启动插件服务，接收作业软件的交互命令
		'''
		self.server = NetworkServer('test-server')
		
		addr = self.conf.get('pluginserver',('localhost',12006))
		
		self.svcplugin = PluginService(self,'pluginserver',addr )
		self.server.addService(self.svcplugin)
		enable = self.conf.get('xproxy.debug',False)
		self.svcplugin.start(enableproxy=enable) #插件服务
		
	
	def getConf(self):
		return self.conf

	handle=None
	@classmethod
	def instance(cls):
		if cls.handle == None:
			cls.handle = cls()
		return cls.handle
	
app = QtGui.QApplication(sys.argv) 
ld= ImagePlayApp.instance().main()
app.exec_()
