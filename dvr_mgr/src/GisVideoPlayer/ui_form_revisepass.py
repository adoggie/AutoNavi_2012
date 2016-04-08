# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_revisepass.ui'
#
# Created: Mon Aug 20 13:49:49 2012
#      by: PyQt4 UI code generator 4.9
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
        Frame.resize(250, 200)
        self.groupBox = QtGui.QGroupBox(Frame)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 231, 181))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 54, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 60, 54, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(20, 90, 61, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.edt_passward = QtGui.QLineEdit(self.groupBox)
        self.edt_passward.setGeometry(QtCore.QRect(100, 30, 113, 20))
        self.edt_passward.setObjectName(_fromUtf8("edt_passward"))
        self.edt_newpasswd = QtGui.QLineEdit(self.groupBox)
        self.edt_newpasswd.setGeometry(QtCore.QRect(100, 60, 113, 20))
        self.edt_newpasswd.setObjectName(_fromUtf8("edt_newpasswd"))
        self.edt_confirmpasswd = QtGui.QLineEdit(self.groupBox)
        self.edt_confirmpasswd.setGeometry(QtCore.QRect(100, 90, 113, 20))
        self.edt_confirmpasswd.setObjectName(_fromUtf8("edt_confirmpasswd"))
        self.btn_updatepasswd = QtGui.QPushButton(self.groupBox)
        self.btn_updatepasswd.setGeometry(QtCore.QRect(30, 150, 75, 23))
        self.btn_updatepasswd.setObjectName(_fromUtf8("btn_updatepasswd"))
        self.btn_cancel = QtGui.QPushButton(self.groupBox)
        self.btn_cancel.setGeometry(QtCore.QRect(130, 150, 75, 23))
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.label_diff = QtGui.QLabel(self.groupBox)
        self.label_diff.setGeometry(QtCore.QRect(60, 120, 111, 16))
        self.label_diff.setText(_fromUtf8(""))
        self.label_diff.setObjectName(_fromUtf8("label_diff"))

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "密码修改", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Frame", "修改密码", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frame", "原密码", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Frame", "新密码", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Frame", "确认新密码", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_updatepasswd.setText(QtGui.QApplication.translate("Frame", "确认修改", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_cancel.setText(QtGui.QApplication.translate("Frame", "取消", None, QtGui.QApplication.UnicodeUTF8))

