# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib
import utils

BASE_MB_BYTES = (1024*1024)

class stoZone:
	def __init__(self,node,id,path,tempdir,lowater=500):
		self.id = id
		self.path = path
		self.node = node
		self.tempdir = tempdir
		self.lowater = lowater
		self.maxspace = 0
		self.freespace = 0
		
	#zone 初始化
	def load(self):
		from distutils.dir_util import mkpath
		try:
			mkpath(self.path)
			mkpath(self.tempdir)			
			self.update()
			if self.maxspace ==0:
				return False
		except:
			traceback.print_exc()
			return False
		return True
	
	#update() - 更新存储状况
	def update(self):
		a,u = utils.statevfs(self.path)
		self.maxspace = a
		self.freespace = u
		

	def hash_status(self):
		return {
				'maxspace':int(self.maxspace/BASE_MB_BYTES),
				'freespace': int((self.freespace - self.lowater)/BASE_MB_BYTES),
				'id':self.id,
				'path':self.path,
				'tempdir':self.tempdir,
				'lowater':self.lowater
				}