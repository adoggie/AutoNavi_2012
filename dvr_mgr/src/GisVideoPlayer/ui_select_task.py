# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_select_task.ui'
#
# Created: Thu Aug 16 13:05:40 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.WindowModal)
        Dialog.resize(363, 90)
        Dialog.setModal(True)
        self.cbxTaskes = QtGui.QComboBox(Dialog)
        self.cbxTaskes.setGeometry(QtCore.QRect(80, 20, 257, 22))
        self.cbxTaskes.setObjectName(_fromUtf8("cbxTaskes"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(16, 28, 54, 12))
        self.label.setObjectName(_fromUtf8("label"))
        self.btnOk = QtGui.QPushButton(Dialog)
        self.btnOk.setGeometry(QtCore.QRect(96, 60, 75, 23))
        self.btnOk.setObjectName(_fromUtf8("btnOk"))
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setGeometry(QtCore.QRect(200, 60, 75, 23))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "选择计划任务", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "计划名称", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOk.setText(QtGui.QApplication.translate("Dialog", "选择", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "取消", None, QtGui.QApplication.UnicodeUTF8))

