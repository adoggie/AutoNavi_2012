# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_imagetags.ui'
#
# Created: Thu Aug 16 14:28:37 2012
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
        Dialog.resize(396, 383)
        font = QtGui.QFont()
        font.setPointSize(10)
        Dialog.setFont(font)
        self.listTag = QtGui.QTreeWidget(Dialog)
        self.listTag.setGeometry(QtCore.QRect(0, 36, 389, 233))
        self.listTag.setObjectName(_fromUtf8("listTag"))
        self.listTag.headerItem().setText(0, _fromUtf8("1"))
        self.btnDel = QtGui.QPushButton(Dialog)
        self.btnDel.setGeometry(QtCore.QRect(192, 280, 60, 23))
        self.btnDel.setObjectName(_fromUtf8("btnDel"))
        self.imgThat = QtGui.QLabel(Dialog)
        self.imgThat.setGeometry(QtCore.QRect(4, 276, 173, 101))
        self.imgThat.setStyleSheet(_fromUtf8("background-color: rgb(255, 170, 0);"))
        self.imgThat.setAlignment(QtCore.Qt.AlignCenter)
        self.imgThat.setObjectName(_fromUtf8("imgThat"))
        self.cbxClass2 = QtGui.QComboBox(Dialog)
        self.cbxClass2.setGeometry(QtCore.QRect(268, 8, 120, 22))
        self.cbxClass2.setObjectName(_fromUtf8("cbxClass2"))
        self.cbxClass1 = QtGui.QComboBox(Dialog)
        self.cbxClass1.setGeometry(QtCore.QRect(108, 8, 120, 22))
        self.cbxClass1.setObjectName(_fromUtf8("cbxClass1"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(4, 16, 54, 12))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(232, 16, 54, 12))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(68, 16, 54, 12))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btnFullImage = QtGui.QPushButton(Dialog)
        self.btnFullImage.setGeometry(QtCore.QRect(192, 316, 75, 23))
        self.btnFullImage.setObjectName(_fromUtf8("btnFullImage"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "影像标记", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDel.setText(QtGui.QApplication.translate("Dialog", "删除", None, QtGui.QApplication.UnicodeUTF8))
        self.imgThat.setText(QtGui.QApplication.translate("Dialog", "影像", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "标记分类", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "(小类)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "(大类)", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFullImage.setText(QtGui.QApplication.translate("Dialog", "原始图像", None, QtGui.QApplication.UnicodeUTF8))

