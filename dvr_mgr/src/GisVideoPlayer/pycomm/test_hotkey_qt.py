#!/usr/bin/env python
#coding=utf-8

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import py_win32key
import win32con

from ctypes import c_bool, c_int, WINFUNCTYPE, windll
from ctypes.wintypes import UINT

class Window(QWidget):
	def __init__(self):
		QWidget.__init__(self)

	def handle_win_f3(self,actionKey):
		print "F3"

	def handle_win_f4(self,actionKey):
		print "F4"

class test_hotkey(QApplication):
	def __init__(self,argv):
		QApplication.__init__(self,argv)
		self.keylist = []
		self.hotkey = py_win32key.HotKey_BOX()

		self.win = Window()
		self.win.show()

		cc = py_win32key.KeyItem()
		cc.id = 1
		cc.hWnd = int(self.win.winId())
		cc.fsModifiers = cc.CTRL
		cc.vk = win32con.VK_F3
		b = Window()
		cc.action = b.handle_win_f3

		self.keylist.append(cc)
		a = self.hotkey.Register(self.keylist)
		print a

	def winEventFilter(self,msg):
		self.hotkey.processMsg(msg)
		return False,0

if __name__ == '__main__':
	app = test_hotkey(sys.argv)
	sys.exit(app.exec_())

#
#   本代码为py_win32key的热键的用法示例：
#
# KeyItem类：
#
#	该类定义了向windows注册热键时的对象，以及该对象必须具有的属性，如下:
#
#	KeyItem.id              id属性必须在应用程序中不可重复,默认为None
#	KeyItem.hWnd            hWnd属性为PyQt的窗口句柄，默认为None的情况下仅支持控制台模式的全局热键
#	KeyItem.fsModifiers     fsModifiers属性为控制类热键例如Ctrl/Shift等等，所有的控制类热键已经全部在KeyItem类中定义
#	KeyItem.vk              vk属性为与控制类热键组合的普通键，列入A/B/C/1/2等，为vk赋值时需转化为ASCII码，即ord('A')、ord('1'),\
#							F1-F12按键请使用win32con.VK_F1来赋值
#	KeyItem.action          action为绑定该热键的回调函数，触发时会根据热键的id找出对应的KeyItem对象，并将该对象作为参数传给回调函数
#	KeyItem.delta           对于KeyItem对象的描述等信息（可选），默认为None
#
# HotKey_BOX类：
#
#	该类提供了向windows注册热键，注销热键，以及对热键触发后对绑定的函数进行调用。
#	分别通过HotKey_BOX.Register/HotKey_BOX.Unregister/HotKey_BOX.processMsg实现。
#
#	list *HotKey_BOX.Register(list *)
#		HotKey_BOX.Register函数负责向windows提交并注册全局热键，所需的参数为KeyItem实例的列表，
#		Register函数将向windows注册列表中所有的KeyItem实例，并返回注册失败的实例列表。
#
#	list *HotKey_ BOX.Unregister（list *）
#		HotKey_BOX.Unregister为Register的逆函数，Unregister将会注销list列表中所有与KeyItem.id对应的热键，并返回注销失败的实例列表。
#
#	list *HotKey_BOX.processMsg(msg)
#		在PyQt中的全局热键支持需要在QApplication中重载winEventFilter函数，并在winEventFilter中调用HotKey_BOX.processMsg。
#		processMsg需要参数为winEventFilter的msg，函数主要用于捕获消息，所有的消息都将被送入processMsg，
#       如果消息为热键触发就调用与热键id对应的函数。







