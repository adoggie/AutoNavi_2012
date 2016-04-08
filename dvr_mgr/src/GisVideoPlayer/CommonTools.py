# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import datetime
import re

class QtMethod():
	def __init__(self):
		pass

	@staticmethod
	def initComBoBox(combo,itemDict):
		for userData in itemDict.iterkeys():
			combo.addItem(QString(itemDict[userData]),QVariant(userData))

	@staticmethod
	def insertOneRow(widget,rowline):
		col_count = widget.columnCount()
		row_count = widget.rowCount()
		if col_count <= len(rowline) and col_count >= 0:
			widget.setRowCount(row_count + 1)
			for col in range(col_count):
				try:
					widget.setItem(row_count,col,rowline[col])
				except IndexError:
					pass
					# widget.setItem(row_count,col,QTableWidgetItem(''))
		elif col_count > len(rowline):
			return False

	@staticmethod
	def insertManyRow(widget,datalist):
		# 获取Tab的当前行数以及列数
		if widget.columnCount() >= 0:
			col_count = widget.columnCount()
		row_count = widget.rowCount()       # 获取的行数即为将要插入的第1行

		# 验证每个元素的长度是否超过列数
		for rowline in datalist:
			if len(rowline) > col_count:
				return False

		# 设置行数并插入数据
		widget.setRowCount(row_count + len(datalist))

		for rowline in datalist:
			for col in range(col_count):
				try:
					widget.setItem(row_count,col,rowline[col])
				except IndexError:
					pass
					# widget.setItem(row_count,col,QTableWidgetItem(QString(u'')))
			row_count += 1      # 行数加1

	@staticmethod
	def showhead(widget,namelist):
		# widget.clear()
		widget.setColumnCount(len(namelist))
		header = QStringList()
		for head in namelist:
			header.append(head)
		widget.setHorizontalHeaderLabels(header)
		widget.horizontalHeader().setResizeMode(QHeaderView.Stretch) # 列平均填充

	@staticmethod
	def showError(msg):
		errorMessage = QtGui.QMessageBox(QtGui.QMessageBox.Warning,u'警告',msg,QtGui.QMessageBox.NoButton)
		errorMessage.addButton("OK", QtGui.QMessageBox.AcceptRole)
		errorMessage.exec_()

	@staticmethod
	def showMessage(msg):
		message = QtGui.QMessageBox(QtGui.QMessageBox.Warning,u'信息',msg,QtGui.QMessageBox.NoButton)
		message.addButton("OK", QtGui.QMessageBox.AcceptRole)
		message.exec_()

	@staticmethod
	def Qdate2datetime(date):
		year = date.year()
		month = date.month()
		day = date.day()
		return datetime.datetime(year,month,day,0,0,0)

class CommonMethod():
	def __init__(self):
		pass

	@staticmethod
	def userDefTime(format_str):
		# 返回用户定义的当前时间字符串
		return datetime.datetime.now().strftime(format_str)

	@staticmethod
	def stdTimeNow():
		# 返回标准定义的当前时间字符串
		return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	@staticmethod
	def timeInstance():
		# 返回当前时间的实例
		return datetime.datetime.now()

	@staticmethod
	def addMinutes(srcTime,addend):
		# .replace(tzinfo=None)去除时区
		# 为时间加上指定的分钟
		return srcTime + datetime.timedelta(minutes = addend)

	@staticmethod
	def getTimeDate(srcTime):
		return srcTime.date()

class CommonString():
	def __init__(self):
		pass

	@staticmethod
	def withoutChinese(str):
		# 检查字符串中是否包含中文字符
		p = re.compile("[^\000-\177]+")
		result = p.match(str)
		if not result:
			return True
		else:
			return False




















































