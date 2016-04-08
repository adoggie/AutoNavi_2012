# -*- coding: utf-8 -*-
# playconsole.py
# 播放控制台

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *


import sys,threading,time,datetime,traceback,json

import imgbase,ui_select_task,dbconn,utils


class Form(QtGui.QDialog,ui_select_task.Ui_Dialog):
	def __init__(self,parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setupUi(self)

#		self.connect(self.btnAdd,SIGNAL('clicked()'),self.onTagAdd)
		self.connect(self.btnOk,SIGNAL('clicked()'),self.onOk)
		self.connect(self.btnClose,SIGNAL('clicked()'),self.onClose)
		self.initData()
		self.imageid = None

	def onOk(self):
		if self.cbxTaskes.currentIndex() ==-1:
			return
		taskid = self.cbxTaskes.itemData(self.cbxTaskes.currentIndex()).toInt()[0]
		db = imgbase.AppInstance.instance().app.getDbConn()

		sql ="update core_ImageFile set task_id =%s where id=%s "%(taskid,self.imageid)
		cr = db.cursor()
		cr.execute(sql)
		db.commit()
		self.done(1)

	def onClose(self):
		self.done(0)

	def initData(self):
		db = imgbase.AppInstance.instance().app.getDbConn()
		sql ="select * from core_WorkTask order by name "
		cr = db.cursor()
		cr.execute(sql)
		while True:
			r = dbconn.fetchoneDict(cr)
			if not r:
				break
			id = r['id']
			name = r['name']
			self.cbxTaskes.addItem(QString.fromUtf8(name),id)

	def selectTask(self,imageid):
		self.imageid = imageid
		self.exec_()


#	def closeEvent(self,evt):
#		self.hide()
#		evt.accept()
