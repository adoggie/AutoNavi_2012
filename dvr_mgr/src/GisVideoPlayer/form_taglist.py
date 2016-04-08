# -*- coding: utf-8 -*-


from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pycomm import py_win32key
import win32con
import ui_form_taglist
import imgbase
import CommonTools
import psycopg2 as pg2
import utils
from msg_plugin import *

MAINKEY = 1
SUBKEY = MAINKEY + 1
HEADER_LIST = [u'Key',u'Type']
TAG_HEADER_LIST = [u'BigClass',u'Key',u'SubClass',u'Key']


class FormTagListAdd(QtGui.QFrame,ui_form_taglist.Ui_Dialog):
	def __init__(self):
		super(FormTagListAdd,self).__init__()
		self.setupUi(self)
		self.hide()

		# 属性
		# imgbase.AppInstance.instance().app.getConsoleWnd().getVideoFrame()
		self.setFixedSize(self.width(),self.height())

		self.INSERT_PIC = 'insert into core_tagpicture (id,delta,width,height,image) values (%s,%s,%s,%s,%s)'
		self.INSERT_TAG = 'insert into core_imagetag (image_id,type,delta,lon,lat,time,creator_id,tagpic_id) values (%s,%s,%s,%s,%s,%s,%s,%s)'
		self.ready2db = {}

		# 控件属性
		self.setFixedSize(self.width(),self.height())
		# QTableWidget
		self.tab_bigclass.verticalHeader().setHidden(True)                           # 序号隐藏
		self.tab_bigclass.setSelectionBehavior(QAbstractItemView.SelectRows)         # 单击选中整行
		self.tab_bigclass.setEditTriggers(QAbstractItemView.NoEditTriggers)          # 单元格不能被编辑

		self.tab_subclass.verticalHeader().setHidden(True)
		self.tab_subclass.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab_subclass.setEditTriggers(QAbstractItemView.NoEditTriggers)

		self.tab_target.verticalHeader().setHidden(True)
		self.tab_target.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab_target.setEditTriggers(QAbstractItemView.NoEditTriggers)

		self.allclass = imgbase.AppInstance.instance().tagkeys
		self.mainClassKey = {}
		self.subClassKey = {}

		# 初始化函数
		CommonTools.QtMethod.showhead(self.tab_bigclass,HEADER_LIST)
		CommonTools.QtMethod.showhead(self.tab_subclass,HEADER_LIST)
		CommonTools.QtMethod.showhead(self.tab_target,TAG_HEADER_LIST)
		self.drawBigClass(self.allclass)
		self.tab_bigclass.setCurrentCell(0,0)
		self.drawSubClass()
		self.tab_bigclass.clearSelection()

		# 信号
		self.connect(self.tab_bigclass,SIGNAL('cellClicked(int,int)'),self.drawSubClass)
		self.connect(self.tab_subclass,SIGNAL('cellDoubleClicked(int,int)'),self.addTag2List)
		self.connect(self.edt_search,SIGNAL('textChanged(const QString)'),self.searchRow)
		self.connect(self.tab_target,SIGNAL('cellDoubleClicked(int,int)'),self.deleteLine)

		self.connect(self.btn_add2db,SIGNAL('clicked()'),self.addTag2db)
		self.connect(self.btn_addtag,SIGNAL('clicked()'),self.addTag2List)
		self.connect(self.btn_delete,SIGNAL('clicked()'),self.deleteLine)
		self.connect(self.edt_search,SIGNAL('returnPressed()'),self.addTag2List)
		self.connect(self.btn_cancel,SIGNAL('clicked()'),self.hideTagList)

		key = py_win32key.KeyItem()
		key.id = 1
		key.hWnd = int(self.winId())
		key.fsModifiers = None
		key.vk = win32con.VK_F8
		key.action = self.showWnd

		self.hotkey = py_win32key.HotKey_BOX()
		a = self.hotkey.Register([key])

		imgbase.AppInstance.instance().addHotKey(self.hotkey)

	handle = None
	@classmethod
	def instance(cls):
		if not cls.handle:
			cls.handle = cls()
		return cls.handle

	def hideTagList(self):
		self.tab_target.setRowCount(0)
		self.hide()

	def winEventFilter(self,msg):
		self.hotkey.processMsg(msg)

	def showWnd(self,key):
		if self.isVisible() == False:
			if imgbase.AppInstance.instance().app.getConsoleWnd().isPlaying():
				imgbase.AppInstance.instance().app.getConsoleWnd().doPause()
				self.show()
		else:
			self.tab_target.setRowCount(0)
			self.hide()

	def deleteLine(self,row,col):
		self.tab_target.removeRow(row)
		# del self.ready2db[row]

	def addTag2List(self):
		bigclass_row = self.tab_bigclass.currentRow()
		subclass_row = self.tab_subclass.currentRow()

		if bigclass_row < 0 or subclass_row < 0:
			return False
		else:
			subclass_value = QVariant(self.subClassKey.get(str(self.tab_subclass.item(subclass_row,0).text()))[1])

		listline = []
		listline.append(QTableWidgetItem(self.tab_bigclass.item(bigclass_row,0)))
		listline.append(QTableWidgetItem(self.tab_bigclass.item(bigclass_row,1)))
		listline.append(QTableWidgetItem(self.tab_subclass.item(subclass_row,0)))
		listline.append(QTableWidgetItem(self.tab_subclass.item(subclass_row,1)))

		CommonTools.QtMethod.insertOneRow(self.tab_target,listline)
		self.tab_target.item(self.tab_target.rowCount()-1,3).setData(Qt.UserRole,subclass_value)
		self.tab_target.resizeRowsToContents()

		# 清除所有输入
		self.edt_search.clear()
		self.tab_subclass.clearSelection()
		self.tab_bigclass.clearSelection()

	def addTag2db(self):
		self.db_conn = imgbase.AppInstance.instance().app.getDbConn()
		self.db_cr = self.db_conn.cursor()

		# 插入Tagpic表
		infodict = imgbase.AppInstance.instance().app.getConsoleWnd().getImageTagInfo()
		pic_id = utils.getdbsequence_pg(self.db_conn,'core_tagpicture_id_seq')

		image = [[pic_id,'',infodict['width'],infodict['height'],pg2.Binary(infodict['image'])]]
		self.db_cr.executemany(self.INSERT_PIC,image)
		self.db_conn.commit()

		# 插入Tag表
		tagData = []
		tagline = []
		for row in range(self.tab_target.rowCount()):
			value = self.tab_target.item(row,3).data(Qt.UserRole)
			tagline.append(infodict['imageid'])                       # image_id
			tagline.append(value.toInt()[0])                          # type
			tagline.append('')                                        # delta
			tagline.append(infodict['lon'])                           # lon
			tagline.append(infodict['lat'])                           # lat
			tagline.append(infodict['time'])                          # time
			tagline.append(1)                                         # creator_id
			tagline.append(pic_id)
			tagData.append(tagline)
			tagline = []
		self.db_cr.executemany(self.INSERT_TAG,tagData)
		self.db_conn.commit()
		self.tab_target.setRowCount(0)
		self.hide()



		#发送删除通知到内业软件
		m = MsgPlugin_AddMarker_2()
		m['id'] = infodict['digest']
		m['markers'].append({'id':infodict['imageid'],'time':infodict['time'],'lon':infodict['lon'],'lat':infodict['lat'],'type':value.toInt()[0]})
		imgbase.AppInstance.instance().app.getPluginService().sendMessage(m)

	def searchRow(self):
		current_word = self.edt_search.text()
		# 字符长度超过小类的最大值，直接退出
		if len(current_word) > SUBKEY:
			self.tab_subclass.clearSelection()
			self.tab_bigclass.clearSelection()
			return False

		# 检索大类Key
		bigclass_index = self.mainClassKey.get(str(current_word[:MAINKEY]))
		if bigclass_index > -1 :
			self.tab_bigclass.setCurrentCell(bigclass_index,0)
			self.drawSubClass()
		else:
			self.tab_bigclass.clearSelection()

		# 检索小类Key
		if len(current_word) >= SUBKEY and bigclass_index > -1:
			try:
				subclass_index = self.subClassKey.get(str(current_word[MAINKEY:SUBKEY]))[0]
			except:
				subclass_index = -1
			if subclass_index > -1:
				self.tab_subclass.setCurrentCell(subclass_index,0)
			else:
				self.tab_subclass.clearSelection()
				self.tab_bigclass.clearSelection()

	def drawBigClass(self,rowlist):
		data = []
		line = []
		row_count = 0
		for bigclass in self.allclass:
			line.append(QTableWidgetItem(bigclass['key']))
			# subclass在taglist中的索引编号，以及为了以后的快捷键快速定位行号
			self.mainClassKey[bigclass['key']] = row_count
			line.append(QTableWidgetItem(bigclass['name']))
			data.append(line)
			line = []
			row_count += 1
		CommonTools.QtMethod.insertManyRow(self.tab_bigclass,data)
		self.tab_bigclass.resizeRowsToContents()
		# self.tab_bigclass.resizeColumnsToContents()

	def drawSubClass(self):
		currentKey = self.tab_bigclass.item(self.tab_bigclass.currentRow(),0).text()
		subClassIndex = self.mainClassKey[str(currentKey)]
		subClassList = self.allclass[subClassIndex]['subclass']

		data = []
		line = []
		self.subClassKey = {}
		row_count = 0
		for subclass in subClassList:
			line.append(QTableWidgetItem(subclass['key']))
			# 同bigclass
			self.subClassKey[subclass['key']] = [row_count,subclass['value']]
			line.append(QTableWidgetItem(subclass['name']))
			data.append(line)
			line = []
			row_count += 1
		# 重建表格
		self.tab_subclass.setRowCount(0)
		CommonTools.QtMethod.insertManyRow(self.tab_subclass,data)
		self.tab_subclass.resizeRowsToContents()
		# self.tab_subclass.resizeColumnsToContents()

