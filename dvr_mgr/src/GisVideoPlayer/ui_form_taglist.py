# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_taglist.ui'
#
# Created: Wed Aug 22 15:17:57 2012
#      by: PyQt4 UI code generator 4.9
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
        Dialog.resize(306, 417)
        self.edt_search = QtGui.QLineEdit(Dialog)
        self.edt_search.setGeometry(QtCore.QRect(70, 10, 151, 20))
        self.edt_search.setObjectName(_fromUtf8("edt_search"))
        self.btn_addtag = QtGui.QPushButton(Dialog)
        self.btn_addtag.setGeometry(QtCore.QRect(230, 10, 75, 23))
        self.btn_addtag.setAutoDefault(False)
        self.btn_addtag.setObjectName(_fromUtf8("btn_addtag"))
        self.tab_bigclass = QtGui.QTableWidget(Dialog)
        self.tab_bigclass.setGeometry(QtCore.QRect(10, 60, 141, 201))
        self.tab_bigclass.setObjectName(_fromUtf8("tab_bigclass"))
        self.tab_bigclass.setColumnCount(0)
        self.tab_bigclass.setRowCount(0)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.tab_subclass = QtGui.QTableWidget(Dialog)
        self.tab_subclass.setGeometry(QtCore.QRect(160, 60, 141, 201))
        self.tab_subclass.setObjectName(_fromUtf8("tab_subclass"))
        self.tab_subclass.setColumnCount(0)
        self.tab_subclass.setRowCount(0)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(60, 40, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(220, 40, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.tab_target = QtGui.QTableWidget(Dialog)
        self.tab_target.setGeometry(QtCore.QRect(10, 270, 291, 111))
        self.tab_target.setObjectName(_fromUtf8("tab_target"))
        self.tab_target.setColumnCount(0)
        self.tab_target.setRowCount(0)
        self.btn_add2db = QtGui.QPushButton(Dialog)
        self.btn_add2db.setGeometry(QtCore.QRect(20, 390, 75, 23))
        self.btn_add2db.setAutoDefault(False)
        self.btn_add2db.setObjectName(_fromUtf8("btn_add2db"))
        self.btn_cancel = QtGui.QPushButton(Dialog)
        self.btn_cancel.setGeometry(QtCore.QRect(220, 390, 75, 23))
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.btn_delete = QtGui.QPushButton(Dialog)
        self.btn_delete.setGeometry(QtCore.QRect(120, 390, 75, 23))
        self.btn_delete.setAutoDefault(False)
        self.btn_delete.setObjectName(_fromUtf8("btn_delete"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.edt_search, self.btn_addtag)
        Dialog.setTabOrder(self.btn_addtag, self.btn_add2db)
        Dialog.setTabOrder(self.btn_add2db, self.tab_bigclass)
        Dialog.setTabOrder(self.tab_bigclass, self.tab_subclass)
        Dialog.setTabOrder(self.tab_subclass, self.tab_target)
        Dialog.setTabOrder(self.tab_target, self.btn_cancel)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "添加Tag点", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_addtag.setText(QtGui.QApplication.translate("Dialog", "选定", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "代码检索", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "大类", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "小类", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_add2db.setText(QtGui.QApplication.translate("Dialog", "提交", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_cancel.setText(QtGui.QApplication.translate("Dialog", "取消", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_delete.setText(QtGui.QApplication.translate("Dialog", "删除行", None, QtGui.QApplication.UnicodeUTF8))

