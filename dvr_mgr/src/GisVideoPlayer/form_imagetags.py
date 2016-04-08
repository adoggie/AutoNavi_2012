# -*- coding: utf-8 -*-
# playconsole.py
# 播放控制台

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *


import sys,threading,time,datetime,traceback,json,os,string

import imgbase,ui_imagetags,dbconn,utils
from msg_plugin import *


class FormImageTags(QtGui.QFrame,ui_imagetags.Ui_Dialog):
	def __init__(self):
		QtGui.QFrame.__init__(self)
		self.setupUi(self)
		self.ids={}

#		self.connect(self.btnAdd,SIGNAL('clicked()'),self.onTagAdd)
		self.connect(self.btnDel,SIGNAL('clicked()'),self.onTagDel)
		self.connect(self.listTag,SIGNAL('itemClicked(QTreeWidgetItem*,int)'),self.listTag_itemClicked)
		self.connect(self.btnFullImage,SIGNAL('clicked()'),self.onBtnFullImage)


		self.listTag.setHeaderLabels([u'时间',u'类型',u'位置'])
		self.listTag.resizeColumnToContents(1)

		self.imgid = None
		self.tagfilter=[]

		self.db = imgbase.AppInstance.instance().app.getDbConn()
		self.initData()
		self.hide()
		self.image = None
		self.imgdigest = None

	_handle = None
	@classmethod
	def instance(cls):
		if not cls._handle:
			cls._handle = cls()
		return cls._handle

	def initData(self):

		self.cbxClass1.addItem(u'全部','')
		self.cbxClass2.addItem(u'全部','')
		keys = imgbase.AppInstance.instance().tagkeys
		for n in keys:
			self.cbxClass1.addItem(n['name'],n['key'])
		self.connect(self.cbxClass1,SIGNAL('currentIndexChanged(int)'),self.onClass1_changed)
		self.connect(self.cbxClass2,SIGNAL('currentIndexChanged(int)'),self.onClass2_changed)

	def onBtnFullImage(self):
		if not self.image:
			return
		name = "%s.jpg"%(time.time())
		self.image.save(name)
		os.system(name)

	def onClass1_changed(self,idx):

		self.cbxClass2.clear()
		self.cbxClass2.addItem(u'全部','')
		self.tagfilter = []
		keys = imgbase.AppInstance.instance().tagkeys
		ci = str( self.cbxClass1.itemData(idx).toString() )

		for n in keys:
			if n['key'] == ci:
				for m in n['subclass']:
					self.cbxClass2.addItem(m['name'],m['value'])
					self.tagfilter.append(m['value'])
				self.cbxClass2.setCurrentIndex(0) # means all
				break

#		self.showImageTags(self.imgid)


	def onClass2_changed(self,idx):
		if idx == -1:
			return

		keys = imgbase.AppInstance.instance().tagkeys
		self.tagfilter = []
		if idx == 0: #all
			ci = str( self.cbxClass1.itemData(self.cbxClass1.currentIndex()).toString() )

			for n in keys:
				if n['key'] == ci:
					for m in n['subclass']:
						self.tagfilter.append(m['value'])
					break
		else:
			id = self.cbxClass2.itemData(idx).toInt()[0]
			self.tagfilter.append(id)
		print self.tagfilter
		self.showImageTags(self.imgid,self.imgdigest)

	def onTagAdd(self):
		pass

	def onTagDel(self):
		'''
			tag最后一个时才删除图像
		'''
		ti =  self.listTag.currentItem()
		if not ti:
			return
		if QMessageBox.No == QMessageBox.question(self,u'提示',u'是否确定删除!',QMessageBox.Yes|QMessageBox.No,QMessageBox.No):
			return

		r = self.ids[ti][0]
		id = r['tagpic_id']
		sql =" select count(*) from core_ImageTag   where tagpic_id=%s"%(id,)
		db = self.db
		cur = db.cursor()
		cur.execute(sql)
		cnt = cur.fetchone()[0]
		if cnt== 1:
			sql = "delete from core_TagPicture where id=%s"%id
			cur = db.cursor()
			cur.execute(sql)
		#
		sql = "delete from core_imageTag where id=%s"%(r['id'])
		cur = db.cursor()
		cur.execute(sql)
		db.commit()
		#删除列表项目

		self.listTag.takeTopLevelItem( self.listTag.indexOfTopLevelItem(self.listTag.currentItem())	 )

		#发送删除通知到内业软件
		m = MsgPlugin_DelMarker_2()
		m['id'] = self.imgdigest
		m['markerid'] = r['id']
		imgbase.AppInstance.instance().app.getPluginService().sendMessage(m)

	def closeEvent(self,evt):
		self.hide()


	def listTag_itemClicked(self,ti,col):

		self.imgThat.setPixmap( QPixmap() )
		pic = self.ids[ti][0]['tagpic_id']
		db = imgbase.AppInstance.instance().app.getDbConn()

		sql = "select * from core_TagPicture where id=%s "% pic

		cur = db.cursor()
		cur.execute(sql)
		r = dbconn.fetchoneDict(cur)
		if not r:
			return
#		print dir(r['image'])
		d = str(r['image']) #.getquoted()
		image = QImage()
#		image = QImage(d,r['width'],r['height'],QImage.Format_RGB888)
		image.loadFromData( d,'jpg')
		if not image:
			return
		self.image = image
		image = image.scaled(self.imgThat.width(),self.imgThat.height())
		self.imgThat.setPixmap(QPixmap.fromImage(image))
		gpstime = self.ids[ti][0]['time']
		#开始跳转
		console = imgbase.AppInstance.instance().app.getConsoleWnd()
		if not console.isPlaying():
			print 'Image is Stopped! skipped..'
			return
		console.seekTime(gpstime)




	def getTagTypeDesc(self,id):
		tags = imgbase.AppInstance.instance().tagkeys
		if not tags:
			return ''
		desc = ''
		for n in tags:
			for m in n['subclass']:
				if m['value'] == id:
					desc = n['name'] + '.' + m['name']
					break
		return desc


	def showImageTags(self,imgid,digest=None):
		import string

		if not imgid:
			return

		self.imgid = imgid
		self.imgdigest = digest

		while self.listTag.topLevelItemCount():
			self.listTag.takeTopLevelItem(0)

		db = imgbase.AppInstance.instance().app.getDbConn()
		sql = "select * from core_ImageTag where image_id=%s order by time"%(imgid)
		if  self.tagfilter:
			ss = map(str,self.tagfilter)
			print self.tagfilter
			ss = string.join(ss,',')

			sql = "select * from core_ImageTag where type in (%s) and image_id=%s order by time"%(ss,imgid)

		cur = db.cursor()
		cur.execute(sql)
		self.ids={}
		while True:
			r = dbconn.fetchoneDict(cur)
			if not r:
				break
			desc = self.getTagTypeDesc(r['type'])
			lon = round(r['lon'],4)
			lat = round(r['lat'],4)
			print r['time']
			ts = utils.formatTimestamp2( r['time'] )
			print ts
			txt = ( ts,desc,"%.4f,%.4f"%(lon,lat) )
			ti = QTreeWidgetItem(txt )
			self.listTag.addTopLevelItem(ti)
			self.ids[ti] = [r,ti] #associate data
		#shit
		self.listTag.resizeColumnToContents(1)
		if self.ids:
			self.raise_()
		#发送AddMarker到内业软件接口

	def closeEvent(self,evt):
		self.hide()
#		evt.accept()
