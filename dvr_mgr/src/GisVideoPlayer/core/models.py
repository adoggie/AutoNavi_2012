# -*- coding:utf-8 -*-
from django.db import models

MAXLEN_TINY= 30
MAXLEN_TINY2 = 50
MAXLEN_SHORT= 80
MAXLEN_SHORT2= 160
MAXLEN_NORMAL = 240
MAXLEN_MEDIUM = 320
MAXLEN_LONG = 480

#系统用户
class AppUser(models.Model):
	name =  models.CharField(max_length=MAXLEN_SHORT,db_index=True)
	passwd =  models.CharField(max_length=MAXLEN_SHORT)
	type = models.IntegerField(db_index=True)
	creatime = models.DateTimeField(null=True,db_index=True)
	rights =  models.TextField(null=True)				#权限列表

#路段信息
class Road(models.Model):
	image = models.ForeignKey('ImageFile',null = False)  
	addtime = models.DateTimeField(null=False,db_index=True)  #单据创建时间
	first_mess = models.IntegerField(null =False,db_index=True) 			
	first_node = models.IntegerField(null =False,db_index=True) 			
	second_mess = models.IntegerField(null =False,db_index=True) 			
	second_node = models.IntegerField(null =False,db_index=True) 			
	first_time = models.DateTimeField(null=False,db_index=True)
	second_time = models.DateTimeField(null=False,db_index=True)
	first_lon = models.FloatField()
	second_lon = models.FloatField()
	first_lat = models.FloatField()
	second_lat = models.FloatField()
	gpsdata = models.TextField()	#整个路段数据描述，可以包含经过这个路段所有轨迹点集合(json)
	image_uri = models.CharField(max_length=MAXLEN_SHORT)

#工作计划
class WorkTask(models.Model):
	name =  models.CharField(max_length=MAXLEN_SHORT,db_index=True) #计划任务名称
	comment = models.TextField(null=True)	#描述
	creator = models.ForeignKey(AppUser,db_index=True)	#创建者
	img_st = models.DateTimeField(null=True,db_index=True) #检索影像开始时间
	img_et = models.DateTimeField(null=True,db_index=True) #检索影像结束时间

#是否必须经过检查才能投入使用
class ImageFile(models.Model):
	uri = models.CharField(max_length=MAXLEN_SHORT)	# node.degist
	starttime = models.DateTimeField(null=False,db_index=True)  #单据创建时间
	addtime = models.DateTimeField(null=False,db_index=True)  #单据创建时间
	duration = models.IntegerField(null =False,db_index=True) 	
	node = models.CharField(max_length=MAXLEN_TINY)	# 
	degist = models.CharField(max_length=MAXLEN_SHORT)						#md5
	filesize = models.IntegerField(null =False,db_index=True) 				#byte unit
	removed = models.IntegerField(default=0,db_index=True)   				#0 - 未删除; 1 - 准备删除 ; 2- 已删除
	gpsdata = models.TextField()											#整个数据描述，包含经过这个路段所有轨迹点集合(json)
	wkt = models.TextField()

	visible = models.BooleanField(default=True)								#文件是否可见,影像处理员会将其删除，则不可见
	task = models.ForeignKey(WorkTask,null=True,db_index=True)				#计划任务
	added = models.ForeignKey(AppUser,db_index=True,null=True)				#添加者
	delta = models.TextField(null=True)										#附属信息 ,供扩展检索使用

	checked = models.ForeignKey(AppUser,related_name='appuser_checked',db_index=True,null=True)			#检查者
	check_time =  models.DateTimeField(db_index=True,null=True)  #检查时间
	check_passed = models.BooleanField(default=True)						#是否通过检查
	check_comment = models.TextField(null=True)								#检查未通过原因描述
	operator = models.ForeignKey(AppUser,related_name='appuser_operator',null=True,db_index=True)			#作业员
	operatime = models.DateTimeField(null=True,db_index=True)				#作业时间 ,记录其观看的时间

class ImageFileReady(models.Model):
	node_id = models.CharField(max_length=MAXLEN_SHORT,db_index=True)
	imgpath = models.CharField(max_length=MAXLEN_SHORT2)
	status = models.IntegerField(db_index=True) # 0 - 未转 ； 1- 正在处理 ； 2 - 已转

class TagPicture(models.Model):
	delta = models.TextField(null=True)
	width = models.IntegerField()
	height = models.IntegerField()

#需要增加BLOB存储抓屏数据
# ALTER TABLE core_tagpicture ADD COLUMN image bytea;


#影像标记
#是否必须通过检查才能使用tag
class ImageTag(models.Model):
	image = models.ForeignKey(ImageFile,db_index=True)  					#存储节点系统
	type = models.IntegerField(db_index=True)								#标记类型
	delta = models.TextField(null=True)										#附属信息 ,供扩展检索使用
	lon = models.FloatField()
	lat = models.FloatField() 												#坐标
	time = models.IntegerField()								#影像偏移时间或者gps时间错

	creator = models.ForeignKey(AppUser,db_index=True)						#添加者
	creatime = models.DateTimeField(null=True,db_index=True)

	operator = models.ForeignKey(AppUser,related_name='imgtag_appuser_operator',null=True,db_index=True)			#作业员
	operatime = models.DateTimeField(null=True,db_index=True)				#作业时间
	operate_comment = models.TextField(null=True)							#作业描述

	checked = models.ForeignKey(AppUser,related_name='imgtag_appuser_checked',db_index=True,null=True)			#检查者
	check_time =  models.DateTimeField(db_index=True,null=True)  	#检查时间
	check_passed = models.IntegerField(null = True,default=0)						#是否通过检查
	check_comment = models.TextField(null=True)								#检查未通过原因描述
	tagpic = models.ForeignKey(TagPicture,db_index=True)


class ImageCheckLog(models.Model):
	task = models.ForeignKey(WorkTask,null=True,db_index=True)
	image = models.ForeignKey(ImageFile,db_index=True)
	checked = models.ForeignKey(AppUser,related_name='imgchecklog_appuser_checked',db_index=True,null=True)			#检查者
	check_time =  models.DateTimeField(db_index=True,null=True)  #检查时间
	check_passed = models.BooleanField(default=True)						#是否通过检查
	check_comment = models.TextField(null=True)								#tags标注错误页归入此表

#class ImageTagCheckLog(models.Model):
#	pass


#存储节点服务器
class StoNodeServer(models.Model):
	sid = models.CharField(max_length=MAXLEN_SHORT)			#节点系统编号
	starttime = models.DateTimeField(null=False,db_index=True)  #服务器启动时间
	livetime = models.DateTimeField(null=False,db_index=True)  #最近一次存活时间
	file_ipaddr = models.CharField(max_length=MAXLEN_TINY)	#文件服务网络地址
	file_port = models.IntegerField(null =False) 			#文件服务端口
	media_ipaddr= models.CharField(max_length=MAXLEN_TINY)	#流媒体服务网络地址
	media_port =models.IntegerField(null =False) 			#媒体服务端口
	maxconn = models.IntegerField(null =False,db_index=True) 	#对大并发访问数量
	curconn = models.IntegerField(null =False,db_index=True) 	#当前连接数量
	rebuild = models.IntegerField(null =False,db_index=True) 	#0 - 不用重建； 1 - 需要重建 ； 2 - 重建完成
	rebuilt_time = models.DateTimeField(null=True,db_index=True) #最近一次重建时间

class StoNodeZone(models.Model):
	sid = models.CharField(max_length=MAXLEN_SHORT)		#存储区标示
	node = models.ForeignKey('StoNodeServer',null = False)  	#存储节点系统
	maxspace = models.IntegerField(null =False,db_index=True) 	# 最大存储空间
	freespace = models.IntegerField(null =False,db_index=True) 	# 空闲空间
	livetime = models.DateTimeField(null=False,db_index=True)	# 存活时间
	path = models.CharField(max_length=MAXLEN_SHORT)
	lowater = models.IntegerField()

#文件索引表，可以搬迁到node端，用于快速定位image文件
class StoNodeImageIndex(models.Model):
	node = models.CharField(max_length=MAXLEN_TINY,db_index=True)	#node编号
	zone = models.CharField(max_length=MAXLEN_TINY,db_index=True) #zone编号
	imgdigest = models.CharField(max_length=MAXLEN_TINY2,db_index=True) #digest md5 摘要
	imgpath = models.CharField(max_length=MAXLEN_SHORT2) #文件存储路径
	
class SystemGlobalSettings(models.Model):
	name = models.CharField(max_length=120,db_index = True)
	value = models.TextField(max_length=256) # should be saved as JSON
	brief = models.CharField(max_length=256,null=True)	
	
class SystemLogging(models.Model):
	time = models.DateTimeField(null=False,db_index=True)  #服务器启动时间
	level= models.IntegerField(null =False,db_index=True) 
	target = models.TextField(null=True)
	source = models.TextField(null=True) # saved as JSON
	detail = models.TextField(null=False)	
	
