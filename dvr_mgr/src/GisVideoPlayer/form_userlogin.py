# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import CommonTools
import imgbase
import ui_form_userlogin


class UserLogin(QtGui.QDialog,ui_form_userlogin.Ui_Frame):
	def __init__(self):
		QDialog.__init__(self)
		self.setupUi(self)
#		self.show()

		self.USER_TEST = "select passwd,type,id from core_appuser where name = %s"

		# 控件初始化
		self.setFixedSize(self.width(),self.height())
		self.edt_passward.setEchoMode(QLineEdit.Password)

		# 信号
		self.connect(self.btn_login,SIGNAL('clicked()'),self.userTest)
		self.connect(self.btn_close,SIGNAL('clicked()'),self.exitSystem)

	def userTest(self):
		db_conn = imgbase.AppInstance().instance().app.getDbConn()
		db_cr = db_conn.cursor()

		username = self.edt_username.text().toUtf8().data()
		passward = self.edt_passward.text().toUtf8().data()

		db_cr.execute(self.USER_TEST ,(username,))
		r = db_cr.fetchone()
		if not r:
			CommonTools.QtMethod.showError(u'用户名或密码错误！')
			return
		pwd = r[0]
		if pwd == passward:
			user = imgbase.AppUser()
			user.name = username
			user.passwd = r[0]
			user.type = r[1]
			user.id = r[2]
			imgbase.AppInstance.instance().onUserLogin_Ok(user)
			self.done(1)
		else:
			CommonTools.QtMethod.showError(u'用户名或密码错误！')


	def exitSystem(self):
		self.done(0)
#		imgbase.AppInstance.instance().app.quit()





