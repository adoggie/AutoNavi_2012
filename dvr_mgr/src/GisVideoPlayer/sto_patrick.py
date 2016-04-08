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
import imgbase
import form_taglist


class ImagePlayApp(QApplication):
	def __init__(self, argv):
		QApplication.__init__(self,argv)

		ffmpeg.InitLib()
		self.db = None
		self.svcplugin = None	
		self.conf = None
		self.conf = utils.loadjson('plugin.txt')

		self.main()

		# form_usermgr.UserMgr.instance()

	def winEventFilter(self,msg):
		imgbase.AppInstance.instance().winEventFilter(msg)

		return False,0

	def __del__(self):
		pass    
	
	
	def getDbConn(self):
		import psycopg2 as pg2

		if not self.db:
			db = self.conf['db']
			try:
				self.db = pg2.connect(host=db['host'],database=db['name'],port=db['port'],user=db['user'],password=db['passwd'])
			except:
				print traceback.print_exc()
				self.db = None
		return self.db
	
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

		imgbase.AppInstance.instance().app = self

		#显示登录界面
		import form_userlogin
		f = form_userlogin.UserLogin()
		r = f.exec_()
#		print r
		if r == 0:
#			self.wndquery.close()
#			self.quit()
			QtGui.qApp.quit()
			sys.exit()
			return
#		self.wndquery.show()

		self.wndconsole = PlayConsoleWindow(self)
		self.wndquery = PlayQueryWindow(self)
		self.wndconsole.showWindow(False)

		self.server = NetworkServer('test-server')
		
		addr = self.conf.get('pluginserver',('localhost',12006))
		
		self.svcplugin = PluginService(self,'pluginserver',addr )
		self.server.addService(self.svcplugin)
		enable = self.conf.get('xproxy.debug',False)
		self.svcplugin.start(enableproxy=enable) #插件服务

		

		taglist = utils.loadjson('taglist.txt')
		imgbase.AppInstance.instance().tagkeys = taglist

		self.init_hotkeys()
		form_taglist.FormTagListAdd.instance()



	#系统登录便显示主控界面
	def login(self):
#		self.wndquery.show()
		pass

	
	def getConf(self):
		return self.conf

#	handle=None
#	@classmethod
#	def instance(cls):
#		if cls.handle == None:
#			cls.handle = cls()
#		return cls.handle

	def quit(self):
		self.svcplugin.shutdown()
		QtGui.qApp.quit()

	def init_hotkeys(self):
		pass




app = ImagePlayApp(sys.argv)
app.exec_()

#ld= ImagePlayApp.instance().main()

