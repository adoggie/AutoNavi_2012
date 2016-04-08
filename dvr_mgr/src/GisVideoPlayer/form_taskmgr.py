# coding=utf-8

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import CommonTools
import ui_form_taskmgr
import datetime
import imgbase


HEADER_LIST = [u'序号',u'任务名称',u'创建者']

class TaskMgr(QtGui.QDialog,ui_form_taskmgr.Ui_Frame):
	def __init__(self,parent):
		QDialog.__init__(self,parent)
#		super(TaskMgr,self).__init__()
		self.setupUi(self)
#		self.show()

		# 属性
		self.taskDict = {}
		self.db_conn = imgbase.AppInstance.instance().app.getDbConn()
		self.db_cr = self.db_conn.cursor()
		self.SELECT_TASK = 'select a.id,a.name,a.comment,a.creator_id,a.img_st,a.img_et,b.name from core_worktask a,core_appuser b where b.id = a.creator_id'
		self.DELETE_TASK = 'delete from core_worktask where id = %s'
		self.UPDATE_TASK = "update core_worktask set (name,comment,img_st,img_et) = (%s,%s,%s,%s) where id = %s"
		self.CREATE_TASK = 'insert into core_worktask (name,comment,creator_id,img_st,img_et) values (%s,%s,%s,%s,%s)'
		self.SELECT_IMG = 'select id from core_imagefile where task_id = %s'


		# 控件初始化
		self.setFixedSize(self.width(),self.height())
		self.AttrPage.setCurrentIndex(0)
		# QTableWidget
		self.tab_taskmgr.verticalHeader().setHidden(True)
		self.tab_taskmgr.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab_taskmgr.setEditTriggers(QAbstractItemView.NoEditTriggers)
		CommonTools.QtMethod.showhead(self.tab_taskmgr,HEADER_LIST)
		# QDateTime
		self.date_endtime.setDate(QDate(2012,11,1))
		self.date_starttime.setDate(QDate(2012,11,1))
		self.date_newendtime.setDate(QDate(2012,11,1))
		self.date_newstarttime.setDate(QDate(2012,11,1))

		# 函数初始化
		self.drawTabTask()

		# 信号
		self.connect(self.btn_addtask,SIGNAL('clicked()'),self.changePage)
		self.connect(self.btn_deltask,SIGNAL('clicked()'),self.deleteTask)
		self.connect(self.btn_resetting,SIGNAL('clicked()'),self.resettingTask)
		self.connect(self.btn_saveinfo,SIGNAL('clicked()'),self.saveInfo)
		self.connect(self.btn_newsaveinfo,SIGNAL('clicked()'),self.insert2DB)
		self.connect(self.btn_cancel,SIGNAL('clicked()'),self.changePage)
		self.connect(self.btn_close,SIGNAL('clicked()'),self.closeWnd)

		self.connect(self.tab_taskmgr,SIGNAL('cellClicked(int,int)'),self.viewTask)

	def closeWnd(self):
		self.close()

	def changePage(self):
		if not self.AttrPage.currentIndex():
			self.AttrPage.setCurrentIndex(1)
		else:
			self.AttrPage.setCurrentIndex(0)

	def insert2DB(self):
		taskname = self.edt_newtaskname.text().toUtf8().data()
		comment = self.txtedt_newtaskmark.toPlainText().toUtf8().data()
		creator_id = imgbase.AppInstance.instance().user.id
		img_st = CommonTools.QtMethod.Qdate2datetime(self.date_newstarttime.date())
		img_et = CommonTools.QtMethod.Qdate2datetime(self.date_newendtime.date())
		if img_st.year > 2000 and img_et.year > 2000:
			self.db_cr.execute(self.CREATE_TASK,(taskname,comment,creator_id,img_st,img_et))
			self.db_conn.commit()
			self.drawTabTask()
		else:
			CommonTools.QtMethod.showError(u'请选择正确时间起止日期')
		self.changePage()

	def saveInfo(self):
		row = self.tab_taskmgr.currentRow()
		db_seq = int(self.tab_taskmgr.item(row,0).text())
		taskname = self.edt_taskname.text().toUtf8().data()
		comment = self.txtedt_taskmark.toPlainText().toUtf8().data()
		img_st = CommonTools.QtMethod.Qdate2datetime(self.date_starttime.date())
		img_et = CommonTools.QtMethod.Qdate2datetime(self.date_endtime.date())
		if img_st.year > 2000 and img_et.year > 2000:
			self.db_cr.execute(self.UPDATE_TASK,(taskname,comment,img_st,img_et,db_seq))
			self.db_conn.commit()
			CommonTools.QtMethod.showMessage(u'成功修改')
			self.drawTabTask(row)
		else:
			CommonTools.QtMethod.showError(u'请选择正确时间起止日期')

	def resettingTask(self):
		self.viewTask(self.tab_taskmgr.currentRow(),0)

	def deleteTask(self):
		DB_seq = int(self.tab_taskmgr.item(self.tab_taskmgr.currentRow(),0).text())
		self.db_cr.execute(self.SELECT_IMG % DB_seq)
		relate_img = self.db_cr.fetchone()
		if relate_img == None:
			self.db_cr.execute(self.DELETE_TASK % DB_seq)
			self.db_conn.commit()
			self.drawTabTask()
		else:
			CommonTools.QtMethod.showError(u'请移除与该任务关联的影像')

	def viewTask(self,row,col):
		taskDetail = self.taskDict.get(row,None)
		if taskDetail != None:
			self.edt_taskname.setText(QString.fromUtf8(taskDetail[1]))
			self.edt_editor.setText(QString.fromUtf8(taskDetail[-1]))
			if taskDetail[4] != None:
				self.date_starttime.setDate(QDate(taskDetail[4].year,taskDetail[4].month,taskDetail[4].day))
			else:
				self.date_starttime.setDate(QDate(2012,1,1))
			if taskDetail[5] != None:
				self.date_endtime.setDate(QDate(taskDetail[5].year,taskDetail[5].month,taskDetail[5].day))
			else:
				self.date_endtime.setDate(QDate(2012,1,1))
			self.txtedt_taskmark.setText(QString.fromUtf8(taskDetail[2]))

	def drawTabTask(self,default = 0):
		self.db_cr.execute(self.SELECT_TASK)
		taskList = self.db_cr.fetchall()
		taskline = []
		taskDate = []
		seq_count = 0
		for task in taskList:
			self.taskDict[seq_count] = task
			seq_count += 1
			# taskline.append(seq_count)
			taskline.append(QTableWidgetItem(str(task[0])))
			taskline.append(QTableWidgetItem(QString.fromUtf8(task[1])))
			taskline.append(QTableWidgetItem(QString.fromUtf8(task[-1])))
			taskDate.append(taskline)
			taskline = []
		self.tab_taskmgr.setRowCount(0)
		CommonTools.QtMethod.insertManyRow(self.tab_taskmgr,taskDate)
		self.tab_taskmgr.resizeRowsToContents()

		# 默认显示第一行的任务信息
		self.tab_taskmgr.setCurrentCell(default,0)
		self.viewTask(default,0)







































