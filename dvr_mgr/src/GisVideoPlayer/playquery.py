# -*- coding: utf-8 -*-
# playconsole.py
# 播放控制台

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ctypes
from ctypes import *

import sys,threading,time,datetime,traceback,string,json
from  ui_management import *
from msg_ctrl import *
from mediasvr import *
from msg_plugin import * 
import ffmpeg

from network import *
from pycomm import mesh2coord
import imgbase
import dbconn


class PlayQueryWindow(QtGui.QMainWindow,Ui_MainWindow):
	def __init__(self,app):
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		self.app = app
		self.show()
		self.connmgr = None #与master的连接
		self.session = None

		self.connect(self.btnDoQuery,SIGNAL('clicked()'),self.btnDoQuery_clicked)
#		self.connect(self.ckShowAll,SIGNAL('stateChanged (int)'),self.ckShowAll_checked)
		#self.connect(self.listRecords,SIGNAL('itemChanged(QTreeWidgetItem*,int)'),self.listRecords_itemChanged)

		self.connect(self.listRecords,SIGNAL('itemClicked(QTreeWidgetItem*,int)'),self.listRecords_itemClicked)
		self.connect(self.listRecords,SIGNAL('itemDoubleClicked(QTreeWidgetItem*,int)'),self.listRecords_itemDblClicked)


	#		self.connect(self.btnOpenMap,SIGNAL('clicked()'),self.btnOpenMap_clicked)
		self.connect(self.btnAbout,SIGNAL('clicked()'),self.btnAbout_clicked)

#		self.connect(self.edtMessId,SIGNAL('textChanged(QString)'),self.edtMessIdChanged)
		self.connect(self.ckShowPlayWnd,SIGNAL('clicked()'),self.evtShowPlayWnd)

		self.connect(self.btnSetMessRect,SIGNAL('clicked()'),self.updateMessRect)

		self.connect(self.btnShowTags,SIGNAL('clicked()'),self.onBtnShowTagsWindow)

		self.connect(self.btnRemove,SIGNAL('clicked()'),self.onBtnRemove)
		self.connect(self.btnMoveToTask,SIGNAL('clicked()'),self.onBtnMoveToTask)
		self.connect(self.btnRemoveFromTask,SIGNAL('clicked()'),self.onBtnRemoveFromTask)
		self.connect(self.btnImagePlay,SIGNAL('clicked()'),self.onBtnImagePlay)

		self.connect(self.miUserMgr,SIGNAL('triggered(bool)'),self.onMenuUserMgr)
		self.connect(self.miTask,SIGNAL('triggered(bool)'),self.onMenuTask)
		self.connect(self.miServerStatus,SIGNAL('triggered(bool)'),self.onMenuServerStatus)
		self.connect(self.miChangePwd,SIGNAL('triggered(bool)'),self.onMenuChangePwd)
		self.connect(self.miExit,SIGNAL('triggered(bool)'),self.onExit)

		self.initUi()
		self.initData()
		self.mtxthis = threading.Lock()

	def onMenuUserMgr(self):
		import form_usermgr
		f = form_usermgr.UserMgr(self)
		f.exec_()

	def onExit(self):
		self.close()

	def onMenuTask(self):
		import form_taskmgr
		f = form_taskmgr.TaskMgr(self)
		f.exec_()

	def onMenuServerStatus(self):
		import form_statistics
		f = form_statistics.SystemStatistics(self)
		f.exec_()

	def onMenuChangePwd(self):
		import form_resivepass
		f = form_resivepass.ResivePass(self)
		f.exec_()




#	从系统中删除影像
	def onBtnRemove(self):
		ti = self.listRecords.currentItem()
		if not ti:
			return
		if QMessageBox.No == QMessageBox.question(self,u'提示',u'是否确定删除!',QMessageBox.Yes|QMessageBox.No,QMessageBox.No):
			return
		id = self.idxdata[ti][0]['id']
		db = imgbase.AppInstance.instance().app.getDbConn()
		sql = "update core_imagefile set removed=1 where id=%s"%(id)
		cur = db.cursor()
		cur.execute(sql)
		db.commit()


	def onBtnMoveToTask(self):
		ti = self.listRecords.currentItem()
		if not ti:
			return
		import form_select_task
		id = self.idxdata[ti][0]['id']
		f = form_select_task.Form(self)
		print f.selectTask(id)


	def onBtnRemoveFromTask(self):
		ti = self.listRecords.currentItem()
		if not ti:
			return
		if QMessageBox.No == QMessageBox.question(self,u'提示',u'是否确定从当前计划任务中移除？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No):
			return

		id = self.idxdata[ti][0]['id']
		db = imgbase.AppInstance.instance().app.getDbConn()
		sql = "update core_imagefile set task_id=null where id=%s"%(id)
		cur = db.cursor()
		cur.execute(sql)
		db.commit()

	def onBtnImagePlay(self):
		ti = self.listRecords.currentItem()
		if not ti:
			return
		self.listRecords_itemDblClicked(ti,0)

#	显示标记窗体
	def onBtnShowTagsWindow(self):
		import form_imagetags
		form_imagetags.FormImageTags.instance().showNormal()
		form_imagetags.FormImageTags.instance().raise_()
		form_imagetags.FormImageTags.instance().show()

	def initTaskList(self):
		#加载计划任务
		self.cbxImageSet.addItem(u'------ 全部 ------',0)

		#db = imgbase.AppInstance.instance().
		db = self.app.getDbConn()
		sql ="select * from core_WorkTask order by name "
		cr = db.cursor()
		cr.execute(sql)
		while True:
			r = dbconn.fetchoneDict(cr)
			if not r:
				break
			id = r['id']
			name = r['name']
			self.cbxImageSet.addItem(QString.fromUtf8(name),id)
#		print self.cbxImageSet.itemData(1).toInt()[0]

	def initData(self):
		self.idxdata={}
		self.initTaskList()

		from pycomm import py_win32key
		import win32con

		self.hotkey = py_win32key.HotKey_BOX()

		key = py_win32key.KeyItem()
		key.id = 10
		key.hWnd = int(self.winId())
		key.fsModifiers = None
		key.vk = win32con.VK_F9
		key.action = self.hotkeyAction_f9
		self.hotkey.Register([key])

		key = py_win32key.KeyItem()
		key.id = 11
		key.hWnd = int(self.winId())
		key.fsModifiers = None
		key.vk = win32con.VK_F10
		key.action = self.hotkeyAction_f10
		self.hotkey.Register([key])

		imgbase.AppInstance.instance().addHotKey(self.hotkey)


	def hotkeyAction_f9(self,key):
		import form_imagetags
		if form_imagetags.FormImageTags.instance().isVisible():
			form_imagetags.FormImageTags.instance().hide()
		else:
			form_imagetags.FormImageTags.instance().showNormal()
			form_imagetags.FormImageTags.instance().raise_()
			form_imagetags.FormImageTags.instance().show()

	def hotkeyAction_f10(self,key):
		v = self.app.getConsoleWnd().isVisible()
		self.app.getConsoleWnd().showWindow(not v )

	def updateMessRect(self):
		rc = mesh2coord.mesh2coord( str(self.edtMessId.text()) )

		if rc:
			rc[2] = rc[0]+rc[2]
			rc[3] = rc[1]+rc[3]
			rc = map(str,rc)
			self.edtGeoRect.setText(','.join(rc))

	def closeEvent(self,evt):
		self.quit()
		self.app.quit()


	def evtShowPlayWnd(self):
		v = self.app.getConsoleWnd().isVisible()
		self.app.getConsoleWnd().showWindow(not v )


#	图幅编号改变，修改地理搜索视野
	def edtMessIdChanged(self,text):
		rc=()

		if rc:
			rc = map(str,rc)
			self.edtGeoRect.setText(','.join(rc))

	def btnOpenMap_clicked(self):
		import webbrowser
		id = self.app.getPluginService().getProxy().getSessionId()
		url = 'http://sw2us.com/sites/default/files/flex/mapdemo.swf?id=%s'%id
		print url
		webbrowser.open(url)
		
	def btnAbout_clicked(self):
#		txt = u'高德软件 上海数据部 \nbin.zhang@autonavi.com tel\n2012.3'
		txt =u'''DVR影像系统 v0.2.0
---------------------------------------
高德软件 上海数据部
bin,ccj,dtr,lnn
June.2012
'''
		QMessageBox.about(self,u"关于..",txt)
		pass
		
	def initUi(self):
		self.listRecords.setHeaderLabels([u'序号',u'影像ID',u'影像时间',u'时长',u'文件长度',u'存储服务器',u'位置',u'标记数量',u'计划任务'])
		#self.listRecords.setHorizontalHeaderLabels(['a','b'])
		self.listRecords.resizeColumnToContents(0)
		self.setStatusBar(None)

		
	def listRecords_itemChanged(self,ti,col):
		print 'click item'
	
	def listRecords_itemClicked(self,ti,col):
		d,ti = self.idxdata[ti]
		m = MsgPlugin_ImagePathSelected_2()
		m['id'] = d['digest']
		self.app.getPluginService().sendMessage(m)
		#----------
		import form_imagetags
		id = d['id']
		w = form_imagetags.FormImageTags.instance()
#		if not w.isVisible():
#			return

		w.showImageTags(id,d['digest'])
#		w.raise_()

#	双击记录进行播放
	def listRecords_itemDblClicked(self,ti,col):
		d,ti = self.idxdata[ti]

		#digest = d['digest']
		#tick = d['starttime']

		gpsdata = d['gpsdata']
		console = self.app.getConsoleWnd()
		console.showWindow(True)
		profile = console.getPlayProfile()
		if profile.get('image_uri')!= d['digest']:
			console.doStop() #停止播放
			console.setPlayProfile({'image_uri':d['digest'],
									'server':d['nodesvc'],
									'gpsdata':gpsdata,
									'id':d['id']
									})
			console.doPlay()
		else:
			if not console.isPlaying():
				console.doPlay()



	def ckShowAll_checked(self,int):
		pass
	
	def btnDoQuery_clicked(self):
		self.doQuery()
		
	def recvEvent(self,evt):		
		if evt.type == NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				self.dispatchMsg(m,evt.conn)
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			print 'connection lost!'
			self.eventConnDisconnected(evt.conn)
	
	def dispatchMsg(self,m,conn):
		print m.getMsg()
		if m.getMsg() == 'mgr_queryresult_networkimage':
			print time.time()
			self.onQueryResult_NetworkImage(m,conn)
			self.btnDoQuery.setEnabled(True)
			print time.time()
			return

	CC=0
	# 查询返回记录
	def onQueryResult_NetworkImage(self,m,conn):
		self.mtxthis.acquire()
		try:
			print 'onquery netwokimages..'
			self.listRecords.clear()
			self.idxdata={}
			self.CC+=1
			results = m.attrs['results']

			cc=1
			for r in results:
				starttime = utils.formatTimestamp2(r['starttime'])
				m = r['duration']//60
				s = r['duration']%60
				nodeid = str(r['nodeid'])
				filesize = r['filesize']
				nodesvc = r['nodesvc']
				filesize = "%.0f MB"%(utils.formatfilesize(filesize))
				#filesize = "%f MB"%(utils.formatfilesize(filesize))
				txt = (str(cc),r['digest'][:6],starttime,"%02d:%02d"%(m,s),
					   filesize,nodeid,nodesvc[0],
					   str(r['tagnum']),
						r['taskname'])

	#			print r.keys()
				ti = QTreeWidgetItem(txt )
				self.listRecords.addTopLevelItem(ti)
				self.idxdata[ti] = [r,ti] #associate data
				cc+=1

			#清除所有轨迹
			m = MsgPlugin_ClearImagePath_2()
			self.app.getPluginService().sendMessage(m)
			#加载在所有路段到地图上
			self.loadImagePathIntoMap(self.idxdata.values())
		except:
			traceback.print_exc()

		self.mtxthis.release()

	#将查询返回的image记录推送到作业软件端
	def loadImagePathIntoMap(self,items):
		# images - []
		#INTERVAL
		INTERVAL = 5
		
		for d,ti in items:
			#id - digest
			lines =[]			
			last=None
			gpsdata = []
			try:
				gpsdata = json.loads(d['gpsdata'])
			except:
				traceback.print_exc()
				continue
			points =[]
			for x in gpsdata:
				points.append(x)
				if not last:
					last = x
					continue
				if int(x['time'])-int(last['time'])<INTERVAL:
					continue
				f,s = last,x
				line = {'first':f,'second':s}
				lines.append(line)
				last = x
			#id = d['id']
			m = MsgPlugin_ImagePathShowOnMap_2()
			m['id'] = d['digest']
			m['lines'] = lines
			m['points'] = points
			m['markers'] =d['tags'] #尚未添加标记数据
#			print d['tags']
			self.app.getPluginService().sendMessage(m)
			#print m.attrs

		
	#连接断开了，清除工作
	def eventConnDisconnected(self,conn):		
		self.connmgr = None
		
	def quit(self):
		if self.connmgr:
			self.connmgr.close()
			self.connmgr = None
		imgbase.AppInstance.instance().app.getConsoleWnd().doStop()
		
	def doQuery(self):
		self.listRecords.clear()

		if self.connmgr == None:
			conn = NetConnection(recvfunc = self.recvEvent)
			addr = self.app.conf["ctrlserver"]
			r = conn.connect( addr)
			print addr
			if r == False:
				#QMessageBox(self,'error','master server cannot be reachable!')
				print '	master unreachable...'
				return NETMSG_ERROR_DESTHOST_UNREACHABLE
			self.connmgr = conn
			session ={}
			session['conn'] = conn
			conn.delta = session
			thread = NetConnThread(conn)

			self.session = session
			
		
		#发送查询请求
		start = time.strptime( self.edtStart.text(),'%Y-%m-%d')
		start = time.mktime(start)
		end = time.strptime( self.edtEnd.text(),'%Y-%m-%d')
		end = time.mktime(end)
		
		
		hours = str(self.edtDayHours.text()).split('-')
		sh,eh = map(lambda x: int(x.strip()),hours)
		
		rect = str(self.edtGeoRect.text()).strip().split(',')
		x1,y1,x2,y2 = map(lambda x: float(x.strip()),rect)
		m =MsgMgr_QueryNetworkImage()
		m.attrs['georect']=(x1,y1,x2-x1,y2-y1)
		m.attrs['starttime']= start
		m.attrs['endtime'] = end
		m.attrs['daystarthour'] = sh
		m.attrs['dayendhour'] = eh
		m.attrs['limit'] = self.edtMaxLines.text().toInt()[0]
		m.attrs['taskid'] = self.cbxImageSet.itemData(self.cbxImageSet.currentIndex()).toInt()[0]
		r = self.connmgr.sendMessage(m)
		self.btnDoQuery.setEnabled(False)

	#地理视野改变
	def OnGeoSightChanged(self,rect):
		x,y,w,h = map(lambda i: round(i,4),rect)
		text ="%s,%s,%s,%s"%(x,y,x+w,y+h)
		self.edtGeoRect.setText(text)


	def OnMapImagePathSelected(self,m):
		#图上轨迹段被点击
		digest = m['id']
		tick = m['timestamp']
		#如果当前影像正在播放则进行时间跳跃
		#根据pathid找到对应的记录,使路段记录被选中状态
		d = None
		gpsdata = None
		for r,ti in self.idxdata.values():
			if r['digest'] == digest:
				d = r
				self.listRecords.setCurrentItem(ti)
				#self.emit(SIGNAL('itemClicked(item,col)'),)
				self.listRecords.setFocus(0)
				break
		
		if not d:return
		gpsdata = d['gpsdata']
		console = self.app.getConsoleWnd()
		profile = console.getPlayProfile()
		if profile.get('image_uri')!= d['digest']:
			console.doStop() #停止播放
			console.setPlayProfile({'image_uri':d['digest'],
									'server':d['nodesvc'],
									'gpsdata':gpsdata,
									'id':d['id']
									})
			console.doPlay()
		else:
			if not console.isPlaying():
				console.doPlay()
		console.seekTime(tick)
		print 'seek time:',tick ,type(tick)


	def resizeEvent(self,e):
		w1,h1 = e.oldSize().width(),e.oldSize().height()
		w2,h2 = e.size().width(),e.size().height()
		if w1 <0:
			return
		dw,dh = w2-w1,h2-h1
#		print w1,h1,w2,h2
#		print dw,dh,self.listRecords.width(),self.listRecords.height()
#		print self.listRecords.width()+dw,self.listRecords.height()+dh
		self.listRecords.resize(self.listRecords.width()+dw,self.listRecords.height()+dh)


if __name__=='__main__':
	pass