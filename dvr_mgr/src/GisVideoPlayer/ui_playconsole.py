# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_playconsole.ui'
#
# Created: Wed Mar 21 17:23:29 2012
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConsoleWnd(object):
    def setupUi(self, ConsoleWnd):
        ConsoleWnd.setObjectName(_fromUtf8("ConsoleWnd"))
        ConsoleWnd.resize(578, 104)
        ConsoleWnd.setStyleSheet(_fromUtf8("background-color:qconicalgradient(cx:0, cy:0, angle:135, stop:0 rgba(255, 255, 0, 69), stop:0.375 rgba(255, 255, 0, 69), stop:0.423533 rgba(251, 255, 0, 145), stop:0.45 rgba(247, 255, 0, 208), stop:0.477581 rgba(255, 244, 71, 130), stop:0.518717 rgba(255, 218, 71, 130), stop:0.55 rgba(255, 255, 0, 255), stop:0.57754 rgba(255, 203, 0, 130), stop:0.625 rgba(255, 255, 0, 69), stop:1 rgba(255, 255, 0, 69))"))
        ConsoleWnd.setFrameShape(QtGui.QFrame.StyledPanel)
        ConsoleWnd.setFrameShadow(QtGui.QFrame.Raised)
        self.widget = QtGui.QWidget(ConsoleWnd)
        self.widget.setGeometry(QtCore.QRect(0, 42, 681, 31))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.sliderTimeLine = QtGui.QSlider(self.widget)
        self.sliderTimeLine.setGeometry(QtCore.QRect(10, 8, 561, 20))
        self.sliderTimeLine.setTracking(True)
        self.sliderTimeLine.setOrientation(QtCore.Qt.Horizontal)
        self.sliderTimeLine.setTickPosition(QtGui.QSlider.NoTicks)
        self.sliderTimeLine.setObjectName(_fromUtf8("sliderTimeLine"))
        self.btnZoomIn = QtGui.QPushButton(ConsoleWnd)
        self.btnZoomIn.setGeometry(QtCore.QRect(330, 76, 75, 23))
        self.btnZoomIn.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 127);\n"
"color: rgb(255, 255, 255);"))
        self.btnZoomIn.setObjectName(_fromUtf8("btnZoomIn"))
        self.btnZoomOut = QtGui.QPushButton(ConsoleWnd)
        self.btnZoomOut.setGeometry(QtCore.QRect(410, 76, 75, 23))
        self.btnZoomOut.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 127);\n"
"color: rgb(255, 255, 255);"))
        self.btnZoomOut.setObjectName(_fromUtf8("btnZoomOut"))
        self.btnFullScreen = QtGui.QPushButton(ConsoleWnd)
        self.btnFullScreen.setGeometry(QtCore.QRect(490, 76, 75, 23))
        self.btnFullScreen.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 127);\n"
"color: rgb(255, 255, 255);"))
        self.btnFullScreen.setObjectName(_fromUtf8("btnFullScreen"))
        self.btnStop = QtGui.QPushButton(ConsoleWnd)
        self.btnStop.setGeometry(QtCore.QRect(90, 76, 71, 23))
        self.btnStop.setStyleSheet(_fromUtf8("background-color: rgb(85, 0, 0);\n"
"color: rgb(255, 255, 255);"))
        self.btnStop.setObjectName(_fromUtf8("btnStop"))
        self.btnPlay = QtGui.QPushButton(ConsoleWnd)
        self.btnPlay.setGeometry(QtCore.QRect(10, 76, 71, 23))
        self.btnPlay.setStyleSheet(_fromUtf8("background-color: rgb(85, 0, 0);\n"
"color: rgb(255, 255, 255);"))
        self.btnPlay.setObjectName(_fromUtf8("btnPlay"))
        self.label = QtGui.QLabel(ConsoleWnd)
        self.label.setGeometry(QtCore.QRect(10, 10, 54, 12))
        self.label.setStyleSheet(_fromUtf8("font: 10pt \"微软雅黑\";"))
        self.label.setObjectName(_fromUtf8("label"))
        self.txtImageDesc = QtGui.QLabel(ConsoleWnd)
        self.txtImageDesc.setGeometry(QtCore.QRect(76, 6, 591, 21))
        self.txtImageDesc.setStyleSheet(_fromUtf8("color:rgb(255, 85, 0);\n"
"font: 10pt \"微软雅黑\";"))
        self.txtImageDesc.setObjectName(_fromUtf8("txtImageDesc"))
        self.btnCaptureScreen = QtGui.QPushButton(ConsoleWnd)
        self.btnCaptureScreen.setGeometry(QtCore.QRect(250, 76, 75, 23))
        self.btnCaptureScreen.setStyleSheet(_fromUtf8("background-color: rgb(255, 170, 0);\n"
"color: rgb(255, 255, 255);"))
        self.btnCaptureScreen.setObjectName(_fromUtf8("btnCaptureScreen"))
        self.txtTime1 = QtGui.QLabel(ConsoleWnd)
        self.txtTime1.setGeometry(QtCore.QRect(10, 30, 151, 16))
        self.txtTime1.setStyleSheet(_fromUtf8("font: 12pt \"黑体\";\n"
"color:rgb(0, 0, 127);\n"
""))
        self.txtTime1.setObjectName(_fromUtf8("txtTime1"))
        self.txtTime2 = QtGui.QLabel(ConsoleWnd)
        self.txtTime2.setGeometry(QtCore.QRect(190, 31, 331, 16))
        self.txtTime2.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);\n"
"font: 10pt \"微软雅黑\";"))
        self.txtTime2.setObjectName(_fromUtf8("txtTime2"))

        self.retranslateUi(ConsoleWnd)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWnd)

    def retranslateUi(self, ConsoleWnd):
        ConsoleWnd.setWindowTitle(QtGui.QApplication.translate("ConsoleWnd", "播放控制台", None, QtGui.QApplication.UnicodeUTF8))
        self.btnZoomIn.setText(QtGui.QApplication.translate("ConsoleWnd", "ZOOM +X", None, QtGui.QApplication.UnicodeUTF8))
        self.btnZoomOut.setText(QtGui.QApplication.translate("ConsoleWnd", "ZOOM -X", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFullScreen.setText(QtGui.QApplication.translate("ConsoleWnd", "FullScreen", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStop.setText(QtGui.QApplication.translate("ConsoleWnd", "停止", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPlay.setText(QtGui.QApplication.translate("ConsoleWnd", " 播放", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ConsoleWnd", "影片信息：", None, QtGui.QApplication.UnicodeUTF8))
        self.txtImageDesc.setText(QtGui.QApplication.translate("ConsoleWnd", "Movie 29.5 fps 1440 x 1080p 6000 bps", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCaptureScreen.setText(QtGui.QApplication.translate("ConsoleWnd", "截屏", None, QtGui.QApplication.UnicodeUTF8))
        self.txtTime1.setText(QtGui.QApplication.translate("ConsoleWnd", "[ 00:00 / 15:00 ] ", None, QtGui.QApplication.UnicodeUTF8))
        self.txtTime2.setText(QtGui.QApplication.translate("ConsoleWnd", "[ 20110318 12:00:00 - 20110318 12:00:15 ]", None, QtGui.QApplication.UnicodeUTF8))

