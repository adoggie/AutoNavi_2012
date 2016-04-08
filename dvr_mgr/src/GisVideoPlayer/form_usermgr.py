# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import CommonTools
import ui_form_usermgr
import imgbase
import datetime

import psycopg2 as pg2

USERNAME_LENGHT = 1
PASSWARD_LENGHT = 6
HEADER_LIST = [u'序号',u'用户名',u'类别']

class UserMgr(QtGui.QDialog,ui_form_usermgr.Ui_Frame,imgbase.AppUserTypes):
	def __init__(self,parent):
		QDialog.__init__(self,parent)
#		super(UserMgr,self).__init__()
		self.setupUi(self)
#		self.show()
		self.AttrPage.setCurrentIndex(0)


		self.USER_NAME = 'select * from core_appuser where name = %s'
		self.USER_LIST = 'select * from core_appuser'
		self.INSERT_USER = 'insert into core_appuser (name,passwd,type,creatime) values (%s,%s,%s,%s)'
		self.DEL_USER = 'delete from core_appuser where name = %s'
		self.UPDATE_USER = 'update core_appuser set (name,passwd,type) = (%s,%s,%s) where id = %s'

		# 属性
		self.db_conn = imgbase.AppInstance.instance().app.getDbConn()
		self.db_cr = self.db_conn.cursor()

		self.appUserType = imgbase.AppUserTypes()
		self.userType = {}
		self.userType[self.appUserType.ROOT] = u'系统管理员'
		self.userType[self.appUserType.OPERATOR] = u'生产作业员'
		self.userType[self.appUserType.PREVIEWER] = u'影像预处理员'
		self.userType[self.appUserType.PREVIEW_CHKER] = u'影像检查员'
		self.userType[self.appUserType.DATA_CHKER] = u'数据检查员'

		# 控件初始化
		self.setFixedSize(self.width(),self.height())
		# QTableWidget
		self.tab_usermgr.verticalHeader().setHidden(True)                           # 序号隐藏
		self.tab_usermgr.setSelectionBehavior(QAbstractItemView.SelectRows)         # 单击选中整行
		self.tab_usermgr.setEditTriggers(QAbstractItemView.NoEditTriggers)          # 单元格不能被编辑
		# QLineEdit
		self.edt_view_passward.setEchoMode(QLineEdit.Password)
		self.edt_view_createtime.setReadOnly(True)
		self.edt_passward.setEchoMode(QLineEdit.Password)
		self.edt_confirmpass.setEchoMode(QLineEdit.Password)
		self.btn_saveinfo.setEnabled(False)
		# QComboBox
		CommonTools.QtMethod.initComBoBox(self.combo_view_usertype,self.userType)
		CommonTools.QtMethod.initComBoBox(self.combo_usertype,self.userType)

		# 属性初始化
		CommonTools.QtMethod.showhead(self.tab_usermgr,HEADER_LIST)
		self.queryUser()

		# 信号
		self.connect(self.btn_adduser,SIGNAL('clicked()'),self.changePage)
		self.connect(self.btn_cancel,SIGNAL('clicked()'),self.changePage)
		self.connect(self.tab_usermgr,SIGNAL('cellClicked(int,int)'),self.viewUser)
		self.connect(self.btn_saveinfo,SIGNAL('clicked()'),self.createUser)
		self.connect(self.btn_deluser,SIGNAL('clicked()'),self.deleteUser)
		self.connect(self.btn_resetting,SIGNAL('clicked()'),self.resettingUser)
		self.connect(self.btn_revise,SIGNAL('clicked()'),self.updateUser)
		self.connect(self.edt_passward,SIGNAL('textChanged(const QString)'),self.showNoDiff)
		self.connect(self.edt_confirmpass,SIGNAL('textChanged(const QString)'),self.showNoDiff)

#	handle = None
#	@classmethod
#	def instance(cls):
#		if not cls.handle:
#			cls.handle = cls()
#		return cls.handle

	def showNoDiff(self):
		if self.edt_passward.text() == self.edt_confirmpass.text():
			self.btn_saveinfo.setEnabled(True)
		else:
			self.btn_saveinfo.setEnabled(False)

	def updateUser(self):
		row = self.tab_usermgr.currentRow()
		username = str(self.edt_username.text(()))
		passwd = str(self.edt_passward.text())
		usertype = self.self.combo_usertype.itemData(self.combo_usertype.currentIndex()).toInt()[0]
		self.db_cr.execute(self.UPDATE_USER,(username,passwd,usertype,row))
		self.db_conn.commit()
		self.queryUser()

	def resettingUser(self):
		self.viewUser(self.tab_usermgr.currentRow(),0)

	def deleteUser(self):
		userName = self.tab_usermgr.item(self.tab_usermgr.currentRow(),1).text().toUtf8().data()
		self.db_cr.execute(self.DEL_USER,(userName,))
		self.db_conn.commit()
		self.queryUser()

	def createUser(self):
		name = self.edt_username.text().toUtf8().data()
		self.db_cr.execute(self.USER_NAME,(name,))
		if len(self.db_cr.fetchall()) > 0:
			CommonTools.QtMethod.showMessage(u'用户名已存在！')
			return False
		if len(self.edt_username.text()) >= USERNAME_LENGHT and len(self.edt_passward.text()) >= PASSWARD_LENGHT:
			passwd = self.edt_passward.text().toUtf8().data()
			usertype = self.combo_usertype.itemData(self.combo_usertype.currentIndex()).toInt()[0]
			timenow = CommonTools.CommonMethod.timeInstance()
		else:
			CommonTools.QtMethod.showMessage(u'请确认用户名(%s位)与密码(%s位)满足最低长度要求！' %(USERNAME_LENGHT,PASSWARD_LENGHT))
			return False
		self.db_cr.execute(self.INSERT_USER,(name,passwd,usertype,timenow))
		self.db_conn.commit()
		self.edt_username.clear()
		self.edt_passward.clear()
		self.edt_confirmpass.clear()
		self.changePage()
		self.queryUser()

	def viewUser(self,currentRow,currentCol):
		userDetail = self.user_list[currentRow]
		self.edt_view_username.setText(QString.fromUtf8(userDetail[1]))
		self.edt_view_passward.setText(QString(userDetail[2]))
		self.edt_view_createtime.setText(QString(userDetail[4].strftime('%Y-%m-%d %H:%M:%S')))
		self.combo_view_usertype.setCurrentIndex(self.combo_view_usertype.findData(userDetail[3]))

	def queryUser(self):
		self.user_list = {}
		self.db_cr.execute(self.USER_LIST)
		self.user_list = self.db_cr.fetchall()
		self.drawUserTab()

	def changePage(self):
		if not self.AttrPage.currentIndex():
			self.AttrPage.setCurrentIndex(1)
		else:
			self.AttrPage.setCurrentIndex(0)

	def drawUserTab(self):
		line = []
		data = []
		for user in self.user_list:
			line.append(QTableWidgetItem(unicode(user[0])))                     # 序号
			line.append(QTableWidgetItem(QString.fromUtf8(user[1])))              # 用户名
			line.append(QTableWidgetItem(self.userType.get(user[3])))           # 类别
			data.append(line)
			line = []
		self.tab_usermgr.setRowCount(0)
		CommonTools.QtMethod.insertManyRow(self.tab_usermgr,data)
		self.tab_usermgr.resizeRowsToContents()
		# self.tab_usermgr.resizeColumnsToContents()
		self.tab_usermgr.setCurrentCell(0,0)
		self.viewUser(0,0)










































