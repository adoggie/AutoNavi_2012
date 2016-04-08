# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_userlogin.ui'
#
# Created: Fri Aug 17 14:04:26 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName(_fromUtf8("Frame"))
        Frame.resize(374, 299)
        self.edt_username = QtGui.QLineEdit(Frame)
        self.edt_username.setGeometry(QtCore.QRect(140, 140, 141, 20))
        self.edt_username.setObjectName(_fromUtf8("edt_username"))
        self.edt_passward = QtGui.QLineEdit(Frame)
        self.edt_passward.setGeometry(QtCore.QRect(140, 180, 141, 20))
        self.edt_passward.setObjectName(_fromUtf8("edt_passward"))
        self.btn_login = QtGui.QPushButton(Frame)
        self.btn_login.setGeometry(QtCore.QRect(100, 220, 75, 23))
        self.btn_login.setObjectName(_fromUtf8("btn_login"))
        self.btn_close = QtGui.QPushButton(Frame)
        self.btn_close.setGeometry(QtCore.QRect(190, 220, 75, 23))
        self.btn_close.setObjectName(_fromUtf8("btn_close"))
        self.label = QtGui.QLabel(Frame)
        self.label.setGeometry(QtCore.QRect(80, 140, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Frame)
        self.label_2.setGeometry(QtCore.QRect(80, 180, 51, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(Frame)
        QtCore.QObject.connect(self.btn_close, QtCore.SIGNAL(_fromUtf8("clicked()")), Frame.close)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "系统登录", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_login.setText(QtGui.QApplication.translate("Frame", "登录", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_close.setText(QtGui.QApplication.translate("Frame", "退出", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Frame", "用户名", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frame", "密码", None, QtGui.QApplication.UnicodeUTF8))

