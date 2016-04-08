# coding=utf-8

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import imgbase
import CommonTools
import ui_form_revisepass


USERNAME_LENGHT = 4
PASSWARD_LENGHT = 6

class ResivePass(QtGui.QDialog,ui_form_revisepass.Ui_Frame):
	def __init__(self,parent):
		QDialog.__init__(self,parent)
		self.setupUi(self)

		# 属性
		self.SRCPASSWD = 'select passwd from core_appuser where name = %s'
		self.UPDATE_PASSWD = 'update core_appuser set passwd = %s where name = %s'
		self.username = imgbase.AppInstance.instance().user.name

		self.db_conn = imgbase.AppInstance.instance().app.getDbConn()
		self.db_cr = self.db_conn.cursor()

		# 控件初始化
		self.setFixedSize(self.width(),self.height())
		self.edt_passward.setEchoMode(QLineEdit.Password)
		self.edt_newpasswd.setEchoMode(QLineEdit.Password)
		self.edt_confirmpasswd.setEchoMode(QLineEdit.Password)

		# 控件初始化
		self.btn_updatepasswd.setEnabled(False)

		# 信号
		self.connect(self.edt_passward,SIGNAL('textChanged(const QString)'),self.testPasswd)
		self.connect(self.edt_newpasswd,SIGNAL('textChanged(const QString)'),self.testPasswd)
		self.connect(self.edt_confirmpasswd,SIGNAL('textChanged(const QString)'),self.testPasswd)
		self.connect(self.btn_updatepasswd,SIGNAL('clicked()'),self.updatePasswd)
		self.connect(self.btn_cancel,SIGNAL('clicked()'),self.closeResive)

	def closeResive(self):
		self.close()

	def updatePasswd(self):
		passward = str(self.edt_passward.text())
		newpasswd = str(self.edt_newpasswd.text())

		self.db_cr.execute(self.SRCPASSWD,(self.username,))
		srcpasswd = self.db_cr.fetchall()[0][0]
		if srcpasswd == passward:
			self.db_cr.execute(self.UPDATE_PASSWD,(newpasswd,self.username))
			self.db_conn.commit()
			self.edt_confirmpasswd.clear()
			self.edt_newpasswd.clear()
			self.edt_passward.clear()
			self.btn_updatepasswd.setEnabled(False)
			CommonTools.QtMethod.showMessage(u'已修改')
			self.close()
		elif self.srcpasswd != passward:
			self.edt_confirmpasswd.clear()
			self.edt_newpasswd.clear()
			self.edt_passward.clear()
			self.btn_updatepasswd.setEnabled(False)
			CommonTools.QtMethod.showMessage(u'修改失败，原密码错误')
			self.label_diff.setText(u'修改失败，原密码错误')

	def testPasswd(self):
		passward = self.edt_passward.text()
		newpasswd = self.edt_newpasswd.text()
		confirmpasswd = self.edt_confirmpasswd.text()
		if passward.length() < PASSWARD_LENGHT:
			self.label_diff.setText(QString(u'原密码不正确'))
			self.btn_updatepasswd.setEnabled(False)
			return False
		if newpasswd.length() < PASSWARD_LENGHT:
			self.label_diff.setText(QString(u'新密码必须大于6位'))
			self.btn_updatepasswd.setEnabled(False)
			return False
		if newpasswd != confirmpasswd:
			self.label_diff.setText(QString(u'两次输入的密码不相同'))
			self.btn_updatepasswd.setEnabled(False)
			return False

		self.label_diff.clear()
		self.btn_updatepasswd.setEnabled(True)