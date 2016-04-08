# -- coding:utf-8 --
#解码器定义

from aobject import *
import os,os.path,sys,time,datetime
#import codec_ks108
#import codec_ks102

MediaCodecType = MediaDataType

#MediaCodec_KS108 = codec_ks108.MediaCodec_KS108
#MediaCodec_KS102 = codec_ks102.MediaCodec_KS102

class MediaCodec_Base:	
	def __init__(self,type,r_maxsize=1024*10):
		#maxsize - 最大缓存，超过限制将视为无效解码
		self.cdctype =  type
		self.rbuf=''
		self.wbuf=''
		self.rmax = r_maxsize
	
	def encode(self,s):		
		pass
	
	def decode(self,s,conn=None):
		#@return (packets,retry) retry表示解码遇到错误或者数据非法
		#packets - [MediaData_Base,] 同时能解出多种媒体类型数据包，同类型也可能有多个
		packets = []
		retry = True
		return packets,retry
	
	def invalid(self):
		#当解不出合法数据包，或者缓冲过大时认为此解码器失效
		if len(self.rbuf) > self.rmax:
			return True
		return False
	
	#将d数据写入db中
	def save(self,db,d):
		pass
	
	
class MediaCodec_Null(MediaCodec_Base):
	#Null解码器，只是为了支持接口
	def __init__(self):
		MediaCodec_Base.__init__(self,MediaCodecType.NULL)
	
	def encode(self,s):
		return s
	
	def decode(self,s,conn=None):
		return s
	
	#@save: 对象存储
	def save(self,store):
		pass

class MediaCodec_Gps(MediaCodec_Base):
	def __init__(self):
		MediaCodec_Base.__init__(self,MediaCodecType.GPS)
	
	def decode(self,s,conn=None):
		#@return MediaData_Gps or None
		pass


class MediaCodec_Audio(MediaCodec_Base):
	def __init__(self):
		MediaCodec_Base.__init__(self,MediaCodecType.AUDIO)
	
	def decode(self,s,conn=None):
		#@return MediaData_Audio or None
		pass




#简单的模拟gps接收解码器
#gps接收程序解析之后连接本地的TcpService端口，并传送过来
#只有简单的gps数据，模拟端口打开
class MediaCodec_SimpleGps(MediaCodec_Base):
	def __init__(self):
		MediaCodec_Base.__init__(self,MediaCodecType.GPS)
	
	def decode(self,s,conn):
		'''
		消息包格式: hwid,gpstime,lon,lat,satenum,sateused,speed,angle\n
		@return: 	packets,retry
		'''
		#@return 解码出多个消息包，并返回是否
		self.rbuf+=s
		segs = self.rbuf.split('\n')
		retry = True
		packets=[]
		if len(segs):
			self.rbuf = segs[-1] #最后一个不完整的包待下一次解析
			segs = segs[:-1]
			for s in segs:				
				try:
					hwid,gpstime,lon,lat,satenum,sateused,speed,angle = s.split(',')					
					d={'mid':hwid,
							'time':datetime.datetime.now(), #datetime.datetime.fromtimestamp(float(gpstime)),
							'lon':float(lon),
							'lat':float(lat),
							'speed':float(speed),
							'angle':float(angle),
							'type':MediaDataType.GPS,
							'power':0,
							'acc':0,
							'miles':0
							
					}
					packets.append(d) #单一的数据包类型					
				except:
					traceback.print_exc()		
		return packets,retry
	
	#执行设备命令
	def command(self,aom,msg):
		# cmd - object (json decoded)
		#@return:  返回命令串
		cmdstr = ''
		return cmdstr
	
	def save(self,aom,d):
		d['speed'] = d['speed'] * 1.852
		g = aom.gm.AOMData_Gps()
		g.ao = aom.ao.dbobj		
		g.savetime = d['time']
		g.satenum = 0
		g.sateused =0
		g.lon = d['lon']
		g.lat = d['lat']
		g.speed = d['speed']
		g.angle = d['angle']		
		g.save()
		
		t = time.mktime(g.savetime.timetuple())
		d['time'] = t
		print d,g.id
		#此数据需要分派出去
		aom.dispatch(d)
		
	def parse(self,aom,d):
		# do nothing
		#这里有些数据需要自动化处理反馈到设备的消息
		pass
	
		