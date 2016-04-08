# -- coding:utf-8 --
#msg_ipc.py
# 播放客户端与内业软件或demo程序的通信接口 ipc方式
#

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

import message
from message import *

'''
demo系统地图采用swmap做底图，在这之上叠加路网层和影像轨迹层
路网层和轨迹层可以显示和隐藏
两种查询操作方式:
1.选择路段，查询关联影像记录，(路段显示高亮)。选择影像记录，在图上显示影像
的轨迹，同时仅显示一条轨迹。 提供全部显示轨迹的功能(checkbox)
图上选择影像轨迹可以定位到影像记录被选择
2.根据当前地图显示地理区域查询影像记录

'''


class MsgPlugin_Base(MessageBase):
	def __init__(self,type=''):
		MessageBase.__init__(self,type)
		
	def marshall(self):
		d = json.dumps(self.attrs)		
		return d	

	@classmethod
	def unmarshall(cls,d):
		#print 'unmarshall:',d
		txt = d		
		m = MessageBase()
		try:
			m.attrs = json.loads(txt)
			if type(m.attrs) != type({}):
				return None						
		except:
			m = None
		#print 'MsgPlugin_Base.unmarshall ok:',m.attrs,type(m)
		return m

		
#地理显示区域改变 , mapapp -> image_client
#地图改变发送通知到影像客户 
class MsgPlugin_GeoSightChanged_1(MsgPlugin_Base):
	def __init__(self,rc):
		MsgPlugin_Base.__init__(self,'plugin_geosightchanged_1')		
		self.attrs['rect']=[] # {x,y,w,h}

#MsgIpc_MapMoved = MsgIpc_GeoSightChanged

# mapapp -> imageclient
# 地图上选择路段，通知影像播放程序，播放程序将从路段开始位置播放影像
class MsgPlugin_MapRoadSelected_1(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_maproadselected_1')		
		self.attrs['road']={} # {first:{mess,roadid},second:{mess,roadid}}

class MsgPlugin_ImagePathSelected_1(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_imagepathselected_1')		
		self.attrs['id']=None # 轨迹编号
		self.attrs['timestamp'] = 0 #图上选择路段最接近的gps时间

class MsgPlugin_ClearImagePath_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_clearimagepath_2')		
		self.attrs['ids']=[]
		#发送到地图上的轨迹线段用一个id标识 ,ids为空则清除所有的轨迹线段
		#

# imageclient -> mapapp
# 选择影像记录在图上显示出影像的轨迹
# 一旦查询影像记录返回，将在地图上显示所有的行驶轨迹
# 传递的这些连续坐标，以两点一条线段方式load进地图显示，
# 这样每条线段都可以相应用户的点击选择操作
# 这些坐标点的时间颗粒可以控制在间隔5-10秒内
class MsgPlugin_ImagePathShowOnMap_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_showimagepathonmap_2')		
		self.attrs['id']='' # {id,points:[{lon,lat,tick,speed,angle},...]}
		self.attrs['lines']=[] #[{first:{lon,lat,speed,angle,time},second:{..}},..]
		self.attrs['markers'] =[] # [{id,lon,lat,time,type} ,..]
		self.attrs['points'] =[]  # {lon,lat,speed,angle,time}

#选择影像记录，在图上高亮显示轨迹
class MsgPlugin_ImagePathSelected_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_imagepathselected_2')		
		self.attrs['id']=''

#图上显示车辆图标
class MsgPlugin_ShowSymbol_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_showsymbol_2')
		self.attrs['show'] = True #
		self.attrs['pos']={} # {lon,lat,time,speed,angle}


#图上添加轨迹marker标记
class MsgPlugin_AddMarker_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_addmarker_2')
		self.attrs['id'] = None #	image id 影像uri
		self.attrs['markers']=[] # [{id,lon,lat,time,type} ,..]    type - marker标记类型uint32

#删除轨迹marker
class MsgPlugin_DelMarker_2(MsgPlugin_Base):
	def __init__(self):
		MsgPlugin_Base.__init__(self,'plugin_delmarker_2')
		self.attrs['id'] = None 	# image id 影像uri md5 string
		self.attrs['markerid']=None # 标签记录的数据库编号


