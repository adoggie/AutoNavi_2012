#!/usr/bin/env python
#coding=utf-8


import os
import sys
import ctypes
import win32con
from ctypes import wintypes


class KeyItem():
	def __init__(self):
		self.id =           None
		self.hWnd =         None
		self.fsModifiers =  None
		self.vk =           None
		self.action =       None
		self.delta =        None

		self.ALT =  win32con.MOD_ALT
		self.CTRL = win32con.MOD_CONTROL
		self.SHIFT = win32con.MOD_SHIFT
		self.WIN_KEY = win32con.MOD_WIN
		self.SHIFT_ALT = self.CTRL | self.SHIFT
		self.CTRL_ALT = self.CTRL | self.ALT
		self.CTRL_SHIFT = self.CTRL | self.SHIFT
		self.CTRL_SHIFT_ALT = self.CTRL | self.SHIFT | self.ALT

class HotKey_BOX():
	def __init__(self):
		self.byref = ctypes.byref
		self.user32 = ctypes.windll.user32
		self.hotkey_actions = {}

	def Register(self,keylist):
		fail_list = []
		for key in keylist:
			res = self.user32.RegisterHotKey(key.hWnd,key.id,key.fsModifiers,key.vk)
			if res > 0:
				self.hotkey_actions[key.id] = key
			else:
				fail_list.append(key)
		return fail_list

	def Unregister(self,keylist):
		fail_list = []
		for key in keylist:
			res = user32.UnregisterHotKey(key.hWnd,key.id)
			if res > 0:
				del self.hotkey_actions[key.id]
			else:
				fail_list.append(key)
		return fail_list

	def WatchHotKey(self):
		msg = wintypes.MSG ()
		while self.user32.GetMessageA (self.byref(msg), None, 0, 0) != 0:
			if msg.message == win32con.WM_HOTKEY:
				actionKey = self.hotkey_actions.get(msg.wParam)
				if actionKey:
					actionKey.action(actionKey)

			self.user32.TranslateMessage (self.byref(msg))
			self.user32.DispatchMessageA (self.byref(msg))

	def processMsg(self,msg):
		if msg.message == win32con.WM_HOTKEY:
			actionKey = self.hotkey_actions.get(msg.wParam)
			if actionKey:
				actionKey.action(actionKey)

if __name__ == '__main__':
	keylist = []

	aa = KeyItem()
	aa.id = 1
	aa.fsModifiers = aa.ALT
	aa.vk = win32con.VK_F1
	aa.action = handle_win_f3

	keylist.append(aa)

	hot = HotKey_BOX()
	hot.Register(keylist)
	hot.Watch()

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
#	list *HotKey_BOX.processMsg(void)
#		在PyQt中的全局热键支持需要在QApplication中重载winEventFilter函数，并在winEventFilter中调用HotKey_BOX.processMsg。
#		processMsg需要参数为winEventFilter的MSG，函数主要用于捕获消息，所有的消息都将被送入processMsg，
#       如果消息为热键触发就调用与热键id对应的函数。