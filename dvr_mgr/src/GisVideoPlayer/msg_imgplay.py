# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib


import message
from message import *
	
class MsgImagePlay_Init(MessageBase):
	def __init__(self,imageid,seq=0):
		MessageBase.__init__(self,'imageplay_init')
		self.attrs['imageid']=imageid
		self.attrs['sequence'] = seq

class ImageStreamContext:
	def __init__(self):
		self.codec_type=0
		self.codec_id=0
		self.width=0
		self.height= 0 
		self.gopsize=0
		self.pixfmt=0
		self.tb_num=0
		self.tb_den = 0
		self.bitrate = 0
		self.frame_number= 0
	
	def hash(self):
		
		return h

		

class MsgImagePlay_Profile(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageplay_profile')
		self.attrs['duration']=0	#转换为秒传递
		self.attrs['filesize']=0
		self.attrs['sequence'] = 0
		self.attrs['createtime']= 0 #影像开始时间,修改时间减去时长
		self.attrs['videoctx']={}
		self.attrs['audioctx']={}
'''
videoctx = {'codec_type':ctx.codec_type,
			'codec_id':ctx.codec_id,
			'width':ctx.width,
			'height':ctx.height,
			'gopsize':ctx.gopsize,
			'pixfmt':ctx.pixfmt,
			'tb_num':ctx.tb_num,
			'tb_den':ctx.tb_den,
			'bitrate':ctx.bitrate,
			'frame_number':ctx.frame_number,
			'videostream':ctx.videostream
		}
'''
		
		
class MsgImagePlay_Packet(MessageBase):
	def __init__(self,seq =0 ,data=None):
		MessageBase.__init__(self,'imageplay_data')
		self.attrs['duration']=0
		self.attrs['pos']=0
		self.attrs['sequence']=seq
		self.attrs['size']=0
		self.attrs['pts'] = 0
		self.attrs['dts'] = 0
		self.attrs['stream']=0 #流编号
		self.bin = data

class MsgImagePlay_Start(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageplay_start')
		self.attrs['sequence']=0

class MsgImagePlay_Pause(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageplay_pause')
		
class MsgImagePlay_Resume(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageplay_resume')

class MsgImagePlay_End(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageplay_end')

class MsgImagePlay_Seek(MessageBase):
	def __init__(self,secs=0,seq=0):
		MessageBase.__init__(self,'imageplay_seek')
		self.attrs['sequence']=seq
		self.attrs['time'] = secs #跳跃到指定时间
		
		
		
		




if __name__=='__main__':
	pass
	