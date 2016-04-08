# -*- coding:utf-8 -*-

import sys,os,os.path

from pycomm import utils
from pycomm import network
from pycomm import message
from pycomm.message import *
from gisbase import *

#
##如果ao的通信参数改变，需要unload之后再load
##通知das服务器加载ao对象
#class MsgAo_DasLoad_6(MessageBase):
#	def __init__(self):
#		MessageBase.__init__(self,'ao_das_load_6')
#		self.attrs['aoid'] = None
#
##通知das服务器卸载ao对象
#class MsgAo_DasUnload_6(MessageBase):
#	def __init__(self):
#		MessageBase.__init__(self,'ao_das_unload_6')
#		self.attrs['aoid'] = None
#		self.attrs['dasid'] = None



#终端注册反馈
class Msg_Dtu_RegResp(message.MessageBase):
	def __init__(self):
		message.MessageBase.__init__(self,'dtu_reg_resp')
		self.attrs['cmd'] ='AP05'
		self.attrs['track_put_freq']=10		#gps采集跟踪上报时间间隔 (s)
		self.attrs['policy_get_freq']=10	#策略获取时间间隔 (m)

	def encode(self,seq,devid):
		return "%s,%s,%s,%s,%s"%(seq,devid,
									self.attrs['cmd'],
									self.attrs['track_put_freq'],
								 	self.attrs['policy_get_freq']
								)

#终端注册反馈
class Msg_Dtu_PolicyResp(message.MessageBase):
	def __init__(self):
		message.MessageBase.__init__(self,'dtu_policy_resp')
		self.attrs['cmd'] ='AP06'
		self.attrs['sdidx']= 0
		self.attrs['rect']=(0,0,0,0)	# (x,y,w,h)
		self.attrs['time']=(0,0,0,0,0)	# (y,m,d,h1,h2)

	def encode(self,seq,devid):
		return "%s,%s,%s,%s,%s,%s"%(seq,devid,self.attrs['cmd'],
								self.attrs['sdidx'],
								','.join( map(str,self.attrs['rect']) ),
								','.join( map(str,self.attrs['time']) )
		)

#终端复位请求
class Msg_Dtu_Reset(message.MessageBase):
	def __init__(self):
		message.MessageBase.__init__(self,'dtu_reset')
		self.attrs['cmd'] ='AP07'

	def encode(self,seq,devid):
		return "%s,%s,%s,%s,%s,%s"%(seq,devid,self.attrs['cmd'])


class MsgAoModule_Alarm(MessageBase):
	MSG='aom_alarm'
	def __init__(self,type):
		MessageBase.__init__(self,MSG)
		self.attrs['aoid'] = None	#ao对象
		self.attrs['aomid'] =  None	#aom对象
		self.attrs['type'] = type # =>>AlarmType.*
		self.attrs['params']={}

class MsgAoModule_GpsData(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'aom_gpsdata')
		self.attrs['aoid'] = None	#ao对象
		self.attrs['aomid'] =  None	#aom对象
		self.attrs['gps'] = {}