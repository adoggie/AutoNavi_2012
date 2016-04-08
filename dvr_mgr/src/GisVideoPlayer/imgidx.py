# -- coding:utf-8 --

# imgidx.py
# 扫描image，获取

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib
import string,json,datetime
import utils


'''
FileServer 定时删除 未成功传输的文件(依据文件名称) 
文件传输结束，及时从临时目录搬走文件

重建idx: 到影像目录下找到 dat,mov文件，生成trp和 .des文件 ，des文件为json格式，记录此影像是否被索引成功，以及影像其他的数据
trp文件采用trpmapfix产生路段匹配文件 .road ,里面包含了所有影像走过的路段信息
所以一个影像必须具备 .trp,.des,.road,.mov四个文件
.des .trp .road 可以在客户端直接转换好，将这些文件通过一次image_put上传到服务器

服务器在每个zone都设置一个tempdir目录，接收文件之后直接更名文件到正确的存储位置，免去了不同zone拷贝的开销
'''

gApp = None
def getLog():
	return gApp.getLog()

def readImageTimes(imagefile,ffmpeg='ffmpeg.exe'):
	import re
	
	
	rst = () # (creattime,lastmodifytime) timestamp time ticks
	detail = os.popen3('%s -i %s'%(ffmpeg,imagefile) )[2].read()
	tt = re.findall('Duration: (\d{1,2}:\d{1,2}:\d{1,2}\.\d{0,4}),',detail,re.M)
	if tt:
		tt = tt[0]
	else:
		return ()
	h,m,s = map(int, map(float,tt.split(':')) )
	duration_secs =  int ( h*3600 + m * 60 + s)
	lastmodify = os.path.getmtime(imagefile)
	createsecs =  lastmodify - duration_secs
	return (int(createsecs),int(lastmodify))

def convert_mov2wmv(mov,wmv,cmd=''):
	cmd='''c:/dvr_bin/ffmpeg.exe -r 15 -i %s -b 6000k -r 15  %s'''%(mov,wmv)


	cmd = os.path.normpath(cmd)
	getLog().debug('cmd:',cmd)
	os.system(cmd)
	#设置mov的mt为wmv的mt

def regdb_ImageFile(stodir,base,zone,app):
	ff = os.path.join(stodir,base)+'.trp'
	#从.dat生成摘要	
	digest = utils.getfiledigest(ff)
	if not digest:
		getLog().debug('digest make failed!')
		return False# 生成摘要失败
	getLog().debug('digest:',digest)
	#检测image是否存在 ，根据digest
	dbconn = app.getDbConn()
	sql = "select count(*) from core_imagefile where degist=%s"
	cr = dbconn.cursor()
	cr.execute(sql,(digest,))
	r = cr.fetchone()[0]
	if r!=0:
		getLog().debug( 'same file is existed!(with digest)')
		return False
	
	#读取image视频信息
	ff = os.path.join(stodir,base)+'.wmv'

	csec,msec = readImageTimes(ff)
	if csec ==0:
		getLog().debug( 'read image time failed!')
		return False
	
	profile={'starttime':utils.mk_datetime(csec),'duration':msec-csec,
			'uri':app.id+'.'+digest,
			'filesize':os.path.getsize(ff),
			'digest':digest,
			'gpsdata':''}
	
	#读取trp生成gpsdata (json格式)
	trp2 = os.path.join(stodir,base)+'.trp2'
	trp = os.path.join(stodir,base)+'.trp'
	
	cwd = os.getcwd()
	os.chdir('c:/dvr_bin')
	cmd = "%s fixpoint %s %s"%('c:/dvr_bin/trpMapFix.exe',trp,trp2)
	cmd = os.path.normpath(cmd)

	os.system(cmd)
	os.chdir(cwd)
	
	
	fp = open(trp2)
	lines = fp.readlines()
	fp.close()
	gpsdata=[]
	wkt = 'LINESTRING(%s)'
	pts=[]
	for line in lines:
		line = line.strip()
		pp = map(string.strip,line.split(','))
		if len(pp)!=6:
			continue
		lon,lat,timestr,tick,speed,angle = pp
		lon = float(lon)/3600.
		lat = float(lat)/3600.
		lon = round(lon,6)
		lat = round(lat,6)
		tick = int(tick)
		speed = float(speed)
		angle = float(angle)
		gps={
			'lon':lon,'lat':lat,'time':tick,'speed':speed,'angle':angle
			}
		gpsdata.append(gps)
		pts.append( "%s %s"%(lon,lat))
	wkt = wkt%(string.join(pts,',')) #LINESTRING()
	profile['gpsdata']= json.dumps(gpsdata)

	#写入数据库 录像文件
	dbconn = app.getDbConn()
	seq = utils.getdbsequence_pg(dbconn,'core_imagefile_id_seq')
	sql = "INSERT INTO core_imagefile(id, uri, starttime, \
	   addtime, duration, node, degist, filesize, removed, \
	   gpsdata,wkt,visible,check_passed) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
	dbconn = app.getDbConn()
	cur = dbconn.cursor()
	cur.execute(sql,(seq,profile['uri'],
					profile['starttime'],
					datetime.datetime.now(), # add time
					profile['duration'],
					app.id, # node id
					profile['digest'],
					profile['filesize'],
					0, # removed
					profile['gpsdata'],
					wkt,
					True,
					True
					))
	#print profile['gpsdata']
	#写入nodeimageindex	
	sql = "insert into core_StoNodeImageIndex (node,zone,imgdigest,imgpath) values \
		(%s,%s,%s,%s)"
	cr = dbconn.cursor()
	#movpath = os.path.join(stodir,base)+'.mov'
	cr.execute(sql,(app.id,zone.id,digest,ff))
	
	return True

def regdb_Road(stodir,base,zone,app):
	#写入路段信息
	#生成.road
	cwd = os.getcwd()
	os.chdir('c:/dvr_bin')
	trp = os.path.join(stodir,base+'.trp')
	road = os.path.join(stodir,base)+'.road'	
	cmd = "%s matchroad %s %s"%('c:/dvr_bin/trpMapFix.exe',trp,road)
	#路段可能不能被匹配, .road文件大小为0
	getLog().debug( 'Match RoadPart finished!')
	os.system(cmd)
	os.chdir(cwd)
	
	#读出路段信息，写入数据表
	fp = open(road)
	lines = fp.readlines()
	fp.close()
	dbconn = app.getDbConn()
	'''
	// 输出json编码
		s = QString("{\"lon\":%1,\"lat\":%2,\"tick\":%3,\"speed\":%4,\"angle\":%5}").arg(pt.lon,0,'f',6).arg(pt.lat,0,'f',6).arg(pt.timetick).arg(pt.speed).arg(pt.angle);
		s = QString("{\"mess\":%1,\"node\":%2}").arg(node.Mesh_id).arg(node.Node_id);
		s = QString("{\"firstNode\":%1,\"secondNode\":%2,\"firstPoint\":%3,\"secondPoint\":%4}").arg(RoadNodeToStr(part.first_node)).arg(RoadNodeToStr(part.second_node))
	'''
	for line in lines:		
		line = line.strip()
		if not line:continue
		d = json.loads(line.strip())
		
		
		seqroad = utils.getdbsequence_pg(dbconn,'core_road_id_seq')
		
		sql = "INSERT INTO core_road(id, image_id, addtime, first_mess,\
			first_node, second_mess, second_node, first_time, \
			second_time, first_lon, second_lon, first_lat, \
			second_lat,gpsdata, image_uri) \
			values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
		
		cur = dbconn.cursor()
		cur.execute(sql,(seqroad,seq,
						datetime.datetime.now(),
						d['firstNode']['mess'],
						d['firstNode']['node'],
						d['secondNode']['mess'],
						d['secondNode']['node'],
						utils.mk_datetime(d['firstPoint']['tick']),
						utils.mk_datetime(d['secondPoint']['tick']),
						float(d['firstPoint']['lon']),
						float(d['secondPoint']['lon']),
						float(d['firstPoint']['lat']),
						float(d['secondPoint']['lat']),
						line.strip(),
						app.id+'.'+digest))
	return True
		
def isExisted(mov,db):
	name,ext = os.path.splitext(mov)
	ff = name +'.dat'
	#从.dat生成摘要
	digest = utils.getfiledigest(ff)

	#检测image是否存在 ，根据digest
	dbconn = db
	sql = "select count(*) from core_imagefile where degist=%s"
	cr = dbconn.cursor()
	cr.execute(sql,(digest,))
	r = cr.fetchone()[0]
	if r==0:
		return False
	return True

def appendImage(id,mov,zone,app):
	try:
		dbconn = app.getDbConn()
		if isExisted(mov,dbconn): #已经处理的image
			return False

		sql ="update core_ImageFileReady set status=1 where id=%s"
		cr = dbconn.cursor()
		cr.execute(sql,(id,))
		dbconn.commit()

		stodir,name = os.path.split(mov)
		base,ext = os.path.splitext(mov) # xxx  .mov
		wmv = os.path.join(stodir,base)+'.wmv'

		#开始转换
		if os.path.exists(mov):
			if os.path.exists(wmv):
				os.remove(wmv)
			convert_mov2wmv(mov,wmv, app.getConf()['cvtcmd'])
		#删除 .mov , .ready
		time.sleep(0.5)
		mt = utils.getmtime(mov)
		utils.setmtime(wmv,mt)

		if app.getConf().get('remove_mov',False): #删除 .mov 文件
			os.remove(mov)


		trp = os.path.join(stodir,base)+'.trp'
		if not os.path.exists(trp):
			getLog().debug( 'no trp file!')
			return False#不存在 .trp 考虑删除mov文件记录
		ff = os.path.join(stodir,base)+'.dat'
		if not os.path.exists(ff):
			getLog().debug( 'no dat file')
			return False#不存在 .dat

		if not regdb_ImageFile(stodir,base,zone,app):
			return

	#	if not regdb_Road(stodir,base,zone,app):
	#		return

		sql ="update core_ImageFileReady set status=2  where id=%s"
		cr = dbconn.cursor()
		cr.execute(sql,(id,))
		dbconn.commit()
	except:

		getLog().debug('image index error:',mov,traceback.format_exc())
		return False
	return True

#初始化存储区
#将未转换成功的image状态设置为未转换0
def initZone(zone,app):
	global gApp
	gApp = app
	db = app.getDbConn()
	#sql ="delete from  core_ImageFileReady where node_id=%s"
	sql ="update core_ImageFileReady set status=0 where node_id=%s and status=1"
	cr = db.cursor()
	cr.execute(sql,(app.id,))
	db.commit()

#处理失败清除image文件
def clearImage(id,image,zone,app):
	try:
		getLog().debug('deleting image file:',id,image)
		db = app.getDbConn()
		sql ="delete from  core_ImageFileReady where id=%s"

		cr = db.cursor()
		cr.execute(sql,(id,))
		db.commit()
		name,ext = os.path.splitext(image)
		if os.path.exists(image):
			os.remove(image)
		wmv = name+".wmv"
		if os.path.exists(wmv):
			os.remove(wmv)
		trp = name+".trp"
		if os.path.exists(trp):
			os.remove(trp)
		dat = name+".dat"
		if os.path.exists(dat):
			os.remove(dat)
	except:
		getLog().error("clearImage error:",traceback.format_exc())



def buildImageIndex(zone,app):
	db = app.getDbConn()
	sql ="select id,imgpath from core_ImageFileReady where node_id=%s and status =0"
	cr = db.cursor()
	cr.execute(sql,(app.id,))

	while True:
		r = cr.fetchone()
		if not r:break
		id,image = r

		getLog().debug("indexing file:",r[0])
		rc  = appendImage( id,image ,zone,app)
		if not rc:
			clearImage(id,image,zone,app)

#从指定zone上重建影像记录
#这些影像是手动拷贝到zone存储目录
#仅有wmv和trp文件
def rebuildImages_fromlocal(zone,app):
	global gApp
	gApp = app

	zonedir = zone.path
	db = app.getDbConn()
	if not os.path.isdir(zonedir):
		return

	sql ="delete from core_ImageFileReady where node_id=%s"
	cr = db.cursor()
	cr.execute(sql,(zone.id,))
	sql = "delete from core_ImageFile where node=%s"
	cr = db.cursor()
	cr.execute(sql,(zone.id,))

	sql = "delete from core_stonodeimageindex where node=%s"
	cr = db.cursor()
	cr.execute(sql,(zone.id,))


	db.commit()
	#
	files = os.listdir(zonedir)
	for file in files: #存储日期目录一级
		if not os.path.isdir( os.path.join(zonedir,file) ):
			continue
		items = os.listdir(zonedir+'/'+file)
		for item in items:
			try:
				d = os.path.join(zonedir,file,item)
				base,ext = os.path.splitext(d)

				if ext.lower() not in ('.wmv','.trp'):
					#print 'file is dirty! ',d
					continue	#文件不是 wmv和trp一对
				regdb_ImageFile(os.path.join(zonedir,file),base,zone,app)
				print d
				db.commit()
			except:

				getLog().debug( traceback.format_exc().decode('utf8') )
				return


#实现mov直接导入存储节点
def importImageFile(stodir,base,zone,app):
	trp = os.path.join(stodir,base)+'.trp'
	digest = utils.getfiledigest(trp)
	if not digest:
		getLog().debug('digest make failed!')
		return False# 生成摘要失败
	getLog().debug('digest:',digest)
	#检测image是否存在 ，根据digest
	dbconn = app.getDbConn()

	#读取image视频信息
	mov = os.path.join(stodir,base)+'.mov'

	csec,msec = readImageTimes(mov)
	if csec ==0:
		getLog().debug( 'read image time failed!')
		return False

	profile={'starttime':utils.mk_datetime(csec),'duration':msec-csec,
			 'uri':app.id+'.'+digest,
			 'filesize':os.path.getsize(mov),
			 'digest':digest,
			 'gpsdata':''}


	fp = open(trp)
	lines = fp.readlines()
	fp.close()
	gpsdata=[]
	wkt = 'LINESTRING(%s)'
	pts=[]
	for line in lines:
		line = line.strip()
		pp = map(string.strip,line.split(','))
		if len(pp)!=6:
			continue
		lon,lat,timestr,tick,speed,angle = pp
		lon = float(lon)/3600.
		lat = float(lat)/3600.
		lon = round(lon,6)
		lat = round(lat,6)
		tick = int(tick)
		speed = float(speed)
		angle = float(angle)
		gps={
			'lon':lon,'lat':lat,'time':tick,'speed':speed,'angle':angle
		}
		gpsdata.append(gps)
		pts.append( "%s %s"%(lon,lat))
	wkt = wkt%(string.join(pts,',')) #LINESTRING()
	profile['gpsdata']= json.dumps(gpsdata)

	#写入数据库 录像文件
	dbconn = app.getDbConn()
	seq = utils.getdbsequence_pg(dbconn,'core_imagefile_id_seq')
	sql = "INSERT INTO core_imagefile(id, uri, starttime, \
		   addtime, duration, node, degist, filesize, removed, \
		   gpsdata,wkt,visible,check_passed) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
	dbconn = app.getDbConn()
	cur = dbconn.cursor()
	cur.execute(sql,(seq,profile['uri'],
					 profile['starttime'],
					 datetime.datetime.now(), # add time
					 profile['duration'],
					 app.id, # node id
					 profile['digest'],
					 profile['filesize'],
					 0, # removed
					 profile['gpsdata'],
					 wkt,
					 True,
					 True
	))


	sql = "insert into core_StoNodeImageIndex (node,zone,imgdigest,imgpath) values \
			(%s,%s,%s,%s)"
	cr = dbconn.cursor()

	cr.execute(sql,(app.id,zone.id,digest,mov))
	dbconn.commit()

	return True
	
if __name__=='__main__':
	pass
	