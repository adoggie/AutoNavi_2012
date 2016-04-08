# -- coding:utf-8 --
#解码器定义

#from aobject import *
import os,os.path,sys,time,datetime,copy,threading,json
#import codec
from pycomm.message import *
from pycomm import utils
from gisbase import *
from gismsg import *
from pycomm.dbconn import *

#MediaCodecType = MediaDataType
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
	

	
ALARM_TYPELIST={
	0:u'车辆断电',
	1:u'电子围栏入界报警',
	2:u'车辆劫警（SOS求助）',
	3:u'车辆防盗器警报',
	4:u'车辆低速报警',
	5:u'车辆超速报警',
	6:u'电子围栏出界报警'
}

ALARM_TYPELIST={
	0:AlarmType.PowerLost ,# u'车辆断电',
	1:AlarmType.BarrierLimitIn, #u'电子围栏入界报警',
	2:AlarmType.SOS, #u'车辆劫警（SOS求助）',
	3:AlarmType.ROB, #u'车辆防盗器警报',
	4:AlarmType.SpeedLower, #u'车辆低速报警',
	5:AlarmType.SpeedOver, #u'车辆超速报警',
	6:AlarmType.BarrierLimitOut #u'电子围栏出界报警'
}



def parseTime(dmy,hms):
	d,mon,y = map(int, map(float,[dmy[:2],dmy[2:4],dmy[4:]]) )
	h,min,s = map(int, map(float,[hms[:2],hms[2:4],hms[4:]]) )
	#print d,mon,y,h,min,s
	return time.mktime((2000+y,mon,d,h,min,s,0,0,0))

#简单的模拟gps接收解码器
#gps接收程序解析之后连接本地的TcpService端口，并传送过来
#只有简单的gps数据，模拟端口打开
'''
MediaCodec
可以开启工作线程来处理解码工作，令socket服务线程可专注在接收数据处理

'''
class MediaCodec:
	def __init__(self,svc):
		self.buf =''
		self.conn = None
		self.svc = svc
		self.mtx = threading.Lock()
		self.buflist=[]
		self.mtxdecode =threading.Lock()
		self.msgcnt=0 #接收消息计数 
	
	def getLog(self):
		return self.svc.app.getLog()
	
#	def parse_gps(self,msg,s):
#		# gps 数据长度62个字符
#		msg['gps'] = None #AOCTRL_CMD_SIMPLING_GPSDATA
#		if len(s)!=62:
#			print 'gps packet size dirty:',len(s)
#			return
#		try:
#			yy = int(s[:2])
#			mm = int(s[2:4])
#			dd = int(s[4:6])
#			av = s[6]	#是否有效
#			lat = int(s[7:9])+ float( s[9:16]) / 60.
#			ns = s[16] #维度标志 N/S
#			lon = int(s[17:20]) + float( s[20:27]) /60.
#			ew = s[27]
#			speed = float(s[28:33])
#			HH = int(s[33:35])
#			MM = int(s[35:37])
#			SS = int(s[37:39])
#			angle = float(s[39:45])
#			power = int(s[45])
#			if power==1:
#				power=0
#			else:
#				power=1
#
#			acc = int(s[46])
#			mileflag = s[53]
#			miles = int(s[54:],16)/1000.00
#			miles = round(miles,3)
#			#print 2000+yy,mm,dd,HH,MM,SS
#			gpstime = datetime.datetime(2000+yy,mm,dd,HH,MM,SS)
#			#GMT+8
#			gpstime = gpstime + datetime.timedelta(hours=8)
#			if av =='A':
#				av = 1
#			else:
#				av = 0
#			msg['gps'] = {
#				#'time':gpstime,
#				'gpstime':utils.mk_timestamp(gpstime),
#				'satenum':0,
#				'sateused':0,
#				'lon':lon,
#				'lat':lat,
#				'speed':speed,
#				'angle':angle,
#				'power':power,
#				'acc':acc,
#				'miles':miles,
#				'av':av,
#				'systime':int(time.time())
#			}
#		except:
#			traceback.print_exc()
#			msg['gps'] = None


	def parse_gps(self,msg,pp):
		msg['gps'] = None #AOCTRL_CMD_SIMPLING_GPSDATA

		try:
			ymd,hms,lon,lat,speed,angle,sdslot = pp
			print ymd,hms,lon,lat,speed,angle,sdslot

			yy = int(ymd[4:6])
			mm = int(ymd[2:4])
			dd = int(ymd[:2])

			HH = int(hms[:2])
			MM = int(hms[2:4])
			SS = int(hms[4:6])

			lon = int(lon[:3]) + float(lon[3:])/(1000.*60.)
			lat = int(lat[:2]) + float( lat[2:]) /(1000.*60.)

			speed = float(speed)
			angle = float(angle)
			sdslot = int(sdslot)

			gpstime = datetime.datetime(2000+yy,mm,dd,HH,MM,SS)
			#GMT+8
			gpstime = gpstime + datetime.timedelta(hours=8)

			msg['gps'] = {
				#'time':gpstime,
				'gpstime':utils.mk_timestamp(gpstime),
				'satenum':0,
				'sateused':0,
				'lon':lon,
				'lat':lat,
				'speed':speed,
				'angle':angle,
				'power':0,
				'acc':0,
				'miles':0,
				'av':0,
				'systime':int(time.time()),
				'sdslot':sdslot
			}
		except:
			traceback.print_exc()
			msg['gps'] = None

	def parseMessage(self,s):
		# @return:  MsgAoModule_Base()		
		#msg={'mid':self.conn.mid,'cmd':0,'seq':'','params':'','gps':None}	# mid - 模块硬件编号
		pp = s.split(',')
		seq,devid,cmd = pp[:3]
		pp = pp[3:]

		msg = {}
		msg['msg'] = cmd
		msg['seq'] = seq
		msg['rawmsg'] = s

		msg['cmd'] =cmd
#		devid = devid[:4] #取前3位编码
		msg['devid'] = devid

		msg['params']=''

		msg['systime'] = int(time.time())
		msg['gps'] = None
		msg['alarm'] =None


		self.getLog().debug('<<'+s)
		
		msg['mid'] = msg['devid'] #设备编号
		
		if cmd =='BP05':	#注册信息
			pass #self.parse_gps(msg,pp[0])	#解析gps
		elif cmd =='BP06': #终端请求策略
			self.parse_gps(msg,pp)#解析gps
		elif cmd == 'BP08': #报警消息
			pass #self.parse_gps(msg,pp[1])	#解析gps
			#msg['alarm'] = pp[0]
			#msg['params'] = {}
		elif cmd =='BP09' : 		#设备Gps监控轨迹上传
			self.parse_gps(msg,pp)
		else:
			msg = None

		if msg:
			if msg['mid']:
				self.conn.mid = msg['mid'] #设备编码关联		
		return msg	
	
	#数据置入队列,应检查队列长度和数据合法性 
	def queueIn(self,s,conn):
		self.mtx.acquire()
		self.buflist.append(s)
		self.mtx.release()
		return True
		
	PKT_SIGN_HDR='*'
	PKT_SIGN_TAIL='#'
	def decode(self):			
		#@return: 	packets,retry		
		#解码出多个消息包，并返回是否
		#需要枷锁，防止多个线程同时被调度进入执行
		r = self.mtxdecode.acquire(0)
		if not r: #其他线程正被占用
			return (),True #消息为空，处理成功		
		self.mtx.acquire()
		if self.buflist:
			self.buf+= reduce(lambda x,y:x+y,self.buflist)
		self.buflist = []
		self.mtx.release()		
		msglist=[]
		retry = True
		while True:
			p1 = self.buf.find('*')
			if p1 == -1:
				self.buf=''
				break #注意，这里有容错功能
			self.buf = self.buf[p1:]
			
			p2 = self.buf.find('#')
			if p2 == -1:
				if len(self.buf) > 1024:
					return (),False # please break socket connection
				break	# push in more data				
			#find tail
			msg = None
			try:
				msg = self.parseMessage(self.buf[1:p2])
			except:
				traceback.print_exc()
				msg = None
			if msg:
				msglist.append(msg)
			self.buf = self.buf[p2+1:]
			
		self.mtxdecode.release()
		
		return msglist,retry

	#根据传入的消息分拣出gps,alarm消息  MsgAoModule_Alarm(), MsgAoModule_GpsData()
	def filter_msg(self,m,aom):
		ms =[]
		if m['gps']:
			x = MsgAoModule_GpsData()
			x['aoid'] = aom.ao.id
			x['aomid'] = aom.id
			x['gps'] = m['gps']
			x['gps']['systime'] = m['systime']
			x['mid'] = m['mid'] #设备编号
			ms.append(x)
		if m['alarm']:
			x = MsgAoModule_Alarm()
			x['aoid'] = aom.ao.id
			x['aomid'] = aom.id
			x['params'] = m['params']
			x['type'] = m['alarm']
			ms.append(x)
		return ms

	#执行设备命令
	'''
			响应：	中心回应AS01	
			说明：	本消息适用于所有终端。本消息最多发送10次，每次间隔30秒，收到平台响应后不再上发。	
	'''
	def command(self,aom,m,db):
		if not m: return
		code=''
		params=''
		code = m.encode('0000',aom.sid)
		if not code:
			return
		
		code='%s#'%(code)
		try:			
			self.conn.write(code)
			self.getLog().debug('>>'+str(code))
		except:
			traceback.print_exc()
			
	#发送module的配置参数到设备
	def initSettings(self,aom,db):
		try:
			#return True
		
			sql="select settings from giscore_ao_module where id=%s"
			cr = db.cursor()
			cr.execute(sql,(aom.id,))
			r = fetchoneDict(cr)
			if r:
				settings = json.loads(r['settings'])				
				for k,v in settings.items():
					m = None
					if k=='acc_on_freq':
						m = MsgAom_AccOnContinuedSet_5()
						m['value'] = v
					if k=='acc_off_freq':
						m = MsgAom_AccOffContinuedSet_5()
						m['value'] = v
					if k=='sample_contined': #等时回传
						m = MsgAom_ContinuedSet_5()						
						m['freq'] = v.get('freq',0)
						m['duration'] = v.get('duration',0)
					if m:
						time.sleep(5) #必须等待，连续发送将导致不处理，很有可能设备的缓存区过小，或者没有硬件握手，导致数据接收失败
						self.getLog().debug('>>initSetting:'+str(m))
						self.command(aom,m,db)
						
		except:
			traceback.print_exc()
	
	#将d数据写入db中
	# 根据不同的数据进行hash分派 目前之后gps和告警信息进行分派
	# m - MsgAoModule_Base
	def save(self,aom,m,db):
		'''
		保存设备所有信息，不区分是何类型
		'''
		try:
			#如果是连接进入的第一个消息包，读取modle的settings参数，发送到设备
			if self.msgcnt==0:
				self.initSettings(aom,db)
				
			self.msgcnt+=1
			
			
			seq = utils.getdbseq(db,'giscore_ao_modulelog_id_seq')
			sql = "insert into giscore_ao_modulelog (id,ao_id,module_id,type,time,\
				msgtype,params,rawmsg,seq) \
				values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			cr = db.cursor()
			#params = m.marshall()
			params = json.dumps(m['params'])
			cr.execute(sql,(seq,aom.ao.id,
							aom.id,
							ModuleMsgType.DEV2SYS,
							utils.mk_datetime(m['systime']),
							m['msg'],
							params,
							m['rawmsg'],
							0
							))
			db.commit()						
			return True
		except:
			traceback.print_exc()
			return False
		









		
	