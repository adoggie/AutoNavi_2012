# -- coding:utf-8 --


import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading,zlib,json
import datetime
#from Demos.SystemParametersInfo import y
import service
from gismsg import *
from pycomm.dbconn import * 

class MediaDataType:	
	GPS   = 1<<0
	AUDIO = 1<<1
	VIDEO = 1<<2
	IMAGE = 1<<3
	TEXT =  1<<4
	IODATA = 1<<5
	RAWBLOB = 1<<6	
	COMMAND = 1<<7	#通用命令
	ALARM =  1<<8  #报警信息
	UNDEFINED = 0xff



class MediaData_Base:
	def __init__(self,mst):
		self.mst = mst
		self.isdispatch = True #标示此消息是否要进行分派到 cacheserver
	
	def getType(self):
		return self.mst
	
	def getId(self):
		#这里是获得的module id,subclass必须支持
		return ''
	
#MediaData_Gps
#基础的Gps属性
class MediaData_Gps(MediaData_Base):
	def __init__(self):
		MediaData_Base.__init__(self,MediaDataType.GPS)
		self.hwid =''
		self.lon = 0
		self.lat = 0
		self.speed = 0
		self.angle = 0
		self.satenum = 0
		self.sateused = 0
		self.time = 0
		self.power = 0	#电源状态
		self.acc = 0	#点火状态
		self.miles=0	#里程计数
	
	def getId(self):
		return self.hwid #模块的硬件标示
	
	def __unicode__(self):
		return "%s,%s,%s,%s,%s,%s,%s,%s"%(self.hwid,self.lon,self.lat,self.speed,self.angle,self.satenum,self.sateused,self.time)
	
	#编码传输数据(未压缩,未json)
	def hash(self,enctype='json'):
		t = time.mktime(self.time.timetuple())
		s = {'type':MediaDataType.GPS,'hwid':self.hwid,
			 'lon':self.lon,'lat':self.lat,
			 'speed':self.speed,'angle':self.angle,
			 'satenum':self.satenum,'sateused':self.sateused,
			 'time':t,
			 'power':self.power,
			 'acc':self.acc,
			 'miles':self.miles}		
		return s

class MediaData_Command(MediaData_Base):
	def __init__(self,cmd):
		MediaData_Base.__init__(self,MediaDataType.COMMAND)
		MediaData_Base.isdispatch = False 	#默认不需要分派
		self.aoid = 0	#ao对象数据库编号
		self.cmd = cmd #AOCTRL_CMD_XXX
		self.time = time.time() #datetime.datetime.now()
		self.params='' 			#命令控制的参数
		
	
class MediaData_Audio(MediaData_Base):
	G7231 = 1
	GSM610 = 2
	PCM8 = 3
	PCM16 = 4
	
	def __init__(self):
		MediaData_Base.__init__(self,MediaDataType.AUDIO)		

class MediaData_Video(MediaData_Base):
	H264 = 1
	JMPEG = 2
	H263 = 3
	MPEG1 = 4
	MPEG2 = 5
	def __init__(self):
		MediaData_Base.__init__(self)
		self.mst = MediaDataType.VIDEO
	
class MediaData_Image(MediaData_Base):
	PNG = 1
	JPEG = 2
	GIF = 3
	BMP = 4
	UNDEFINE = 0xff
	def __init__(self):
		MediaData_Base.__init__(self)
		self.mst = MediaDataType.IMAGE


class ActiveObject_Module:
	def __init__(self,ao,dbobj):
		self.ao = ao
		#self.type  = type 	#MediaType.*
		self.conn = None	#连接对象
		self.sid = dbobj['dtu_num'] 		#模块对象的硬件标示  ,设备编号+手机号 15位
		self.url = None 	#连接信息
		self.svcname = None
		self.r = dbobj
		self.id = dbobj['id']   #aom_id equals ao_id
	
	def __str__(self):
		return ''
	

#	模块设备断开当前的网络连接
	def disconnect(self):
		try:
			if self.conn:
				self.conn.close()
		except:
			traceback.print_exc()

	def readData(self,m,conn,db=None):
#		print 'enter AoModule::readData'
#		print m,self.sid
		if m['mid'] != self.sid: #硬件编号
#			print 'mid not matched...'
			return False

		conn.aom = self # bind 这里很重要，一个连接与设备模块关联起来了
		self.conn = conn	#保存了便于之后发送消息到设备

		#dtu注册
		if m['cmd'] == 'BP05_':
			d = Msg_Dtu_RegResp()
			self.sendData(d,db)
		elif m['cmd'] == 'BP06': #终端请求策略
			sql = '''select d.*,b.install_date,b.id as vehicle_id,e.area_map as rect from device_dtu a,device_vehicle b,
					strategy_strategy_vechicles_r c, strategy_strategy d,strategy_area e
					where a.id= b.dtu_id and d.area_id = e.id and
					c.vehicle_id = a.id and d.id = c.strategy_id
					and a.dtu_num=%s
				'''
			cr = db.cursor()
			cr.execute(sql,(m['mid'],))
			d = None

			while True:#检索当前有效的策略
				r = fetchoneDict(cr)
				if not r:
					break
				try:
					s,e = str(r['begin_date']),str(r['end_date'])
					print s,e
					s = datetime.datetime.strptime(s,'%Y-%m-%d')
					e = datetime.datetime.strptime(e,'%Y-%m-%d')
					h1,h2 = r['begin_h'],r['end_h']

#					s = s + datetime.timedelta(hours=h1)
#					e = e + datetime.timedelta(hours=h2)
					now = datetime.datetime.now()
					hh = now.hour
					if s<= now and e >= now and h1< hh and h2 > hh:
						instime = datetime.datetime(r['install_date'].year,r['install_date'].month,r['install_date'].day)
						t =  now - instime
						print 'time advance:',t
						d = Msg_Dtu_PolicyResp()
						d['sdidx'] = t.days + 1  # sd array index 计算偏移日期获取索引
						if d['sdidx']< 1 and d['sdidx'] >16: #sd slot invalid
							d = None
							break
						d['rect'] = r['rect'].split(',')	#地理区域
						d['time'] = (now.year,now.month,now.day,h1,h2)

						break
				except:
					traceback.print_exc()
			if d:
				self.sendData(d,db)

#		conn.codec.command(self,m,db) #执行一些必要的反馈
#		conn.codec.save(self,m,db) #写入数据库
		
		#分拣出gps数据和报警数据传递到控制服务器
		ms = conn.codec.filter_msg(m,self)
		for m in ms:
			self.saveData(m,db)		#写入数据库
#			self.ao.app.sendmsg_ctrlsvr(m)

		return True
		
	def saveData(self,m,db):
		now = datetime.datetime.now()
		sql = '''
			select a.id as vehicle_id,b.id as dtu_id from device_vehicle a,device_dtu b where
			a.dtu_id = b.id and b.dtu_num=%s
			'''
		cr = db.cursor()
		cr.execute(sql,(m['mid'],))
		r = fetchoneDict(cr)
		if not r: #dtu并未注册在系统中
			print 'dtu not registered in!',m
			return

		vehicle_id = r['vehicle_id']
		dtu_id = r['dtu_id']
#		print 'saveData(),',m
		if m['msg'] == 'aom_gpsdata': #gps数据 保存
			gps = m['gps']
			if gps:			
				cr = db.cursor()
				sql = '''INSERT INTO gps_log(
						vehicle_id, dtu_id, lon, lat, time, timetick, speed, direction,
						acc, gsm_status, gps_status, host_status, alarm_status, sd_index,av,lon_map,lat_map)
						VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
					'''
				cr.execute(sql,(
								vehicle_id,
								dtu_id,
								gps['lon'],
								gps['lat'],
								datetime.datetime.now(),	#utils.mk_datetime(gps['systime']),
								gps['gpstime'],
								gps['speed'],
								gps['angle'],
								gps['acc'],
								0,
								0,
								0,
								0,
								gps['sdslot'], #sd_index
								gps['av'],
								0,
								0
								))
				db.commit()
		#----- alarm logging ----------------------------
		if m['msg'] == 'aom_alarm': #保存报警消息
			pass

	def sendData(self,d,db):
		try:
			if self.conn == None:
				print 'device is offline!'
				return
			self.conn.codec.command(self,d,db)
		except:
			traceback.print_exc()

	
#active object是个应用概念上的设备对象，运行过程中它将缓存此对象的所有
#接收到的数据，等待其它系统访问、冲刷; 但在对实时性要求比较高的情况下
#ActiveObject要主动提交数据到其它的子系统去 
class ActiveObject_Base:
	#系统对象
	def __init__(self,dbobj,app=None):
		#codecCLS 编解码器类
		self.app = app
		self.modules = [] #通道集合
		self.mtxthis = threading.Lock()
		self.id = dbobj['id']  #数据库对象唯一标示
		self.r = dbobj #giscore.models.ActiveObject
	
	#连接设备或者初始化
	def initModules(self,db):
		#1.加载所有modules
		aom = ActiveObject_Module(self,self.r)
		self.modules.append(aom)


	def addModule(self,m):
		self.modules.append(m)
		
	def getModule(self,type):
		m = None
		try:
			m = self.modules[type]
		except:pass
		return m

	def disconnect(self):
		self.mtxthis.acquire()
		for m in self.modules:
			m.disconnect()
		self.mtxthis.release()



	def readData(self,d,conn,db):
		#@return True - 数据匹配到具体的module设备.else False
		# d - codec解码出来的统一的设备消息,这些消息被分派到module去识别
		r = False
		self.mtxthis.acquire()
		for m in self.modules:
			if m.readData(d,conn,db):
				r = True
				break
		self.mtxthis.release()
		return r
	
	def sendData(self,d,db,module=0):
		'''
			module - module idx
		'''
		self.mtxthis.acquire()
		for aom in self.modules:
			aom.sendData(d,db)
		self.mtxthis.release()

#
#	#执行命令道ao对象
#	def cmdExc(self,module,jsondata):
#		for m in self.modules:
#			if m.type & module: #判断正确的模块类型
#				m.cmdExc(jsondata)
