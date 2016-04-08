# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

import message
from message import *
	
class MsgImagePut_Init(MessageBase):
	def __init__(self,filename='',modifytime=0,filesize=0,md5=''):
		MessageBase.__init__(self,'imageput_init')
		self.attrs['filename']=filename
		self.attrs['modifytime']=modifytime
		self.attrs['filesize']=filesize #单位: mb
		self.attrs['digest']= md5 # 32字符描述 dat文件
		self.attrs['dat']=''
		self.attrs['trp']=''
		
class MsgImagePut_Data(MessageBase):
	def __init__(self,data):
		MessageBase.__init__(self,'imageput_data')
		self.attrs['size']=len(data)
		self.bin = data

class MsgImagePut_End(MessageBase):
	def __init__(self):
		MessageBase.__init__(self,'imageput_end')

Error_Base = 1000
Error_SpaceNotEnough = Error_Base + 1	
	
errors={
	Error_SpaceNotEnough:u'存储空间不够',
}

if __name__=='__main__':
	pass
	