# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_form_statistics
import imgbase
import datetime
import CommonTools



LIVE_TIME = 5
HEADER_LIST_NODE = [u'节点编号',u'节点地址',u'节点状态',u'当前连接数',u'最大空间(GB)',u'剩余空间(GB)',u'剩余空间']
HEADER_LIST_ZONE = [u'节点编号',u'节点地址',u'存储区编号',u'存储区路径',u'最大空间(GB)',u'剩余空间(GB)',u'剩余空间']

class SystemStatistics(QtGui.QDialog,ui_form_statistics.Ui_Frame):
	def __init__(self,parent):
		#super(SystemStatistics,self).__init__(parent)
		QDialog.__init__(self,parent)

		self.setupUi(self)
#		self.setModal(True)
#		self.show()

		# 属性
		self.nodeAdd = {}

		self.db_conn = imgbase.AppInstance.instance().app.getDbConn()
		self.db_cr = self.db_conn.cursor()

		self.MAXSPACE = 'select SUM(b.maxspace) from core_stonodezone b where b.node_id = %s'
		self.FREESPACE = 'select SUM(b.freespace) from core_stonodezone b where b.node_id = %s'
		self.HASKEY = 'select b.node_id from core_stonodezone b where b.node_id = %s'
		self.NODE_QUERY = 'select * from core_stonodeserver'
		self.ZONE_QUERY = 'select * from core_stonodezone where node_id = %s'

		#控件初始化
		self.setFixedSize(self.width(),self.height())
		# QTableWidget
		self.setFixedSize(self.width(),self.height())
		self.tab_node.setSelectionBehavior(QAbstractItemView.SelectRows)         # 单击选中正行
#		self.tab_node.setEditTriggers(QAbstractItemView.NoEditTriggers)          # 单元格不能被编辑
		self.tab_zone.setSelectionBehavior(QAbstractItemView.SelectRows)
#		self.tab_zone.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.tab_zone.verticalHeader().setHidden(True)

		CommonTools.QtMethod.showhead(self.tab_node,HEADER_LIST_NODE)
		CommonTools.QtMethod.showhead(self.tab_zone,HEADER_LIST_ZONE)
		# QLineEdit
		self.edt_onlinenode.setReadOnly(True)
		self.edt_onlinezone.setReadOnly(True)
		self.edt_sysall.setReadOnly(True)
		self.edt_sysavail.setReadOnly(True)
		self.edt_sysfree.setReadOnly(True)

		# 函数
		self.refurbish()

		# 信号
		self.connect(self.btn_refurbish,SIGNAL('clicked()'),self.refurbish)
		self.connect(self.tab_node,SIGNAL('cellClicked(int,int)'),self.drawZone)

	def refurbish(self):
		self.db_cr.execute(self.NODE_QUERY)
		self.nodeInfo = self.db_cr.fetchall()

		nodeDetail = []
		nodeData = []
		sysMax = 0
		sysFree = 0
		self.onlineNode = 0
		self.onlineZone = 0

		self.tab_node.setRowCount(0)
		for node in self.nodeInfo:
			# 节点编号
			nodeDetail.append(QTableWidgetItem(node[1]))

			# 节点地址
			nodeDetail.append(QTableWidgetItem(node[4]))

			# 创建字典，方便Zone快速关联
			self.nodeAdd[node[0]] = [node[1],node[4]]

			# 检查节点的在线情况
			if datetime.datetime.now() < CommonTools.CommonMethod.addMinutes(node[3].replace(tzinfo=None),LIVE_TIME):
				nodeDetail.append(QTableWidgetItem(u'在线'))
				self.onlineNode += 1
			else:
				nodeDetail.append(QTableWidgetItem(u'离线'))
			nodeDetail.append(QTableWidgetItem(unicode(node[8])))

			# 检查该Node是否有对应的Zone
			self.HASKEY = 'select b.node_id from core_stonodezone b where b.node_id = %s'
			self.db_cr.execute(self.HASKEY,(node[0],))
			if self.db_cr.fetchone() == None:
				nodeDetail.append(QTableWidgetItem('-'))
				nodeDetail.append(QTableWidgetItem('-'))
				nodeDetail.append(QTableWidgetItem('-'))
				CommonTools.QtMethod.insertOneRow(self.tab_node,nodeDetail)
				nodeDetail = []
				continue

			# 最大系统总空间
			self.db_cr.execute(self.MAXSPACE,(node[0],))
			maxspace = self.db_cr.fetchall()[0][0]/1024.0
			sysMax += maxspace
			nodeDetail.append(QTableWidgetItem(unicode('%.2f' %maxspace)))

			# 最大系统剩余空间
			self.db_cr.execute(self.FREESPACE,(node[0],))
			freepace = self.db_cr.fetchall()[0][0]/1024.0
			sysFree += freepace
			nodeDetail.append(QTableWidgetItem(unicode('%.2f' %freepace)))

			# 空间利用率
			nodeDetail.append(QTableWidgetItem('%.2f%%' %(freepace/(maxspace*1.0)*100)))

			# 创建Node表
			CommonTools.QtMethod.insertOneRow(self.tab_node,nodeDetail)

			nodeDetail = []

			# 为item关联node_id
			self.tab_node.item(self.tab_node.rowCount() - 1,0).setData(Qt.UserRole,node[0])
		self.tab_node.resizeRowsToContents()

		# 绘制Zone表
		self.drawZone(0,0)

		# 填充edt
		self.edt_sysall.setText(QString(unicode('%.2f' %sysMax)))
		self.edt_sysfree.setText(QString(unicode('%.2f' %sysFree)))
		self.edt_sysavail.setText(QString('%.2f%%' %((sysFree)/(sysMax*1.0)*100)))
		self.edt_onlinenode.setText(QString('%s/%s' %(self.onlineNode,self.tab_node.rowCount())))
		self.edt_onlinezone.setText(QString('%s/%s' %(self.onlineZone,self.tab_zone.rowCount())))

	def drawZone(self,row,col):
		zoneDetail = []
		zoneData = []
		nodeID = self.tab_node.item(row,0).data(Qt.UserRole)
		self.db_cr.execute(self.ZONE_QUERY,(nodeID.toInt()[0],))
		zoneinfo = self.db_cr.fetchall()
		onlineZone = 0
		for zone in zoneinfo:
			zoneDetail.append(QTableWidgetItem(self.nodeAdd[zone[2]][0]))
			zoneDetail.append(QTableWidgetItem(self.nodeAdd[zone[2]][1]))
			zoneDetail.append(QTableWidgetItem(zone[1]))
			zoneDetail.append(QTableWidgetItem(zone[6]))
			zoneDetail.append(QTableWidgetItem(unicode('%.2f' %(zone[3]/1024.0))))
			zoneDetail.append(QTableWidgetItem(unicode('%.2f' %(zone[4]/1024.0))))
			zoneDetail.append(QTableWidgetItem('%.2f%%' %(zone[4]/(zone[3]*1.0)*100)))
			zoneData.append(zoneDetail)
			zoneDetail = []
			if datetime.datetime.now() < CommonTools.CommonMethod.addMinutes(zone[5].replace(tzinfo=None),LIVE_TIME):
				self.onlineZone += 1
		self.tab_zone.setRowCount(0)
		CommonTools.QtMethod.insertManyRow(self.tab_zone,zoneData)
		self.tab_zone.resizeRowsToContents()










































