# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib,threading

import message
from message import *
import network
from network import *
from msg_imgput import *
from msg_ctrl import *


import utils
from fileserv import *
import gs600_trp_2


#<>
import ctypes
import win32api
import win32con
import datetime
kernel32 = ctypes.windll.kernel32
#<>

'''
检索指定目录下 mov和dat文件，dat夹杂在mov的控制头中被传递到服务器
检查mov同级目录下，同名.pass是否存在，表示已经被处理了
1.先转换成trp文件，同dat目录
2.扫描mov文件,并将 mov的../INFO/dat,trp一同传递到服务器存储
生成.pass

'''

class ImageSyncronizer(FileClient):
	def __init__(self):
		FileClient.__init__(self)
		self.lastpercent = 0

	def send(self,addr,mov,indicator=None):
		mov = os.path.normpath(mov)
		if not indicator:
			indicator = self.indicator
		return self.startPut(mov,addr,indicator)

	'''
	beforePut_Init 进行文件合法性检查，包括文件是否能被正常解码；创建时间是否有效；文件时长长是否过短
	 	-- 创建时间在2012年之前视为非法
	 	-- 小于5分钟时长视为非法

	'''
	def beforePut_Init(self,file):
		'''
			file - {filesize,filename,...}
			找寻trp文件并写入 file
			trp在.或者../INFO/.trp|.dat
		'''
		import string
		self.lastpercent = 0

		#文件是否可被解码
		times = utils.readImageTimes(file['filename'])
		if not times: # decode asscess denied
			print 'decode file failed!'
			return False
		st,mt = times
		if st <= 1325350861:#文件创建时间是否合法
			print 'file md time so early!'
			return False
		#文件时长是否过小
		if mt - st < 5*60: # less than 5 minutes, skipped
			print 'file duration too short!'
			return False

		filename = os.path.normpath(file['filename'])
		file['fullname'] = filename
		file['filename'] = os.path.basename(filename)
		#重载文件大小为MB
		file['filesize'] =  int( file['filesize']/ (1024*1024))


		d,b = os.path.split(filename)

		c,ext = os.path.splitext(filename)

		if os.path.exists( c+'.pass'):
			#已处理过了
			print '.pass skipped..'
			return False

		trp = c+'.trp'
		dat= c+'.dat'
		#同级目录是否存在trp和dat
		if os.path.exists( trp): # and os.path.exists( dat):

			pass
		else:#去上级的INFO下检索 dat,trp
			d = d.split(os.path.sep)

			name,ext = os.path.splitext(b)
			trp = string.join(d[:-1],'/')+'/INFO/'+name+'.trp'
			#dat = string.join(d[:-1],'/')+'/INFO/'+name+'.dat'
			if os.path.exists( trp):# and os.path.exists( dat):
				pass
			else:
				print trp
				#print dat
				trp=dat=''
				print '.trp or .dat missed'
				return False #无法找到dat,trp文件
		try:
			#将trp,dat文件内容上传，并将dat内容digest作为资源唯一标示
			fd = open(trp,'rb')
			cont = fd.read()
			fd.close()
			file['trp'] = base64.encodestring(cont)

			print 'trp size:',len(file['trp'])

#			fd = open(dat,'rb')
#			cont = fd.read()
#			fd.close()
#			file['dat'] = base64.encodestring(cont)

			file['digest'] = utils.getfiledigest(trp) #将trp的digest上传 2012.7.17
		except:
			traceback.print_exc()
			print 'create digest failed!'
			return False
		return True

#	做好标记 .pass
	def afterPut_Done(self,file):
		d,ext = os.path.splitext(file['fullname'])
		utils.touchfile( d+".pass")

	def abortPut(self,file):
		pass

	def indicator(self,file):
		''' file - {filesize,sentbytes}
		'''

		num = file['sentbytes']
		den = file['filesize']
		percent = int( (num/float(den))*100) +1
		if percent>100:percent=100
		if self.lastpercent != percent:
			#print num,den
			self.lastpercent = percent
			if percent % 5==0:
				print 'completed %s%%'%(percent)
		#print file['filesize'],file['sentbytes']




mtxobj = utils.MutexObject()

def recvEvent(evt):
	if evt.type == NetConnectionEvent.EVENT_DATA:
		for m in evt.data:
			if m.getMsg() == 'imageput_selectnode_resp':
				mtxobj.notify(m)


	if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
		print 'sto_syncer::connection lost!'

#申请一个存储节点
def applyNodeServer(needspace,server):
	#连接ctrlserver
	conn = NetConnection(recvfunc = recvEvent)
	r = conn.connect( server )
	if not r:
		print 'ctrlserver unreachable!'
		return None
	thread = NetConnThread(conn)
	#发送请求
	needspace = int( needspace/(1024*1024) )
	m = MsgImagePut_SelectNodeRequest(needspace)
	conn.sendMessage(m)

	d = mtxobj.waitObject(5)
	if not d:
		print ' ctrlserver response timeout!'
		return	None
	m = d
	nodeserver = d.attrs['nodeserver'] #获得node服务器地址了
	conn.close()
	return nodeserver





#同步指定目录
#扫描mov文件
'''
检测到如果是2012年之前的mov文件，说明此为未定位文件，直接过滤
'''
def syncDir(dir):
	conf = utils.loadjson('sync.txt')
	if not conf:
		print 'read config failed!'
		return
	#调度一个空闲的nodeserver

	node =None
	if not os.path.exists(dir):
		print 'dir:%s is not reachable!'%dir

	#计算视频总消耗容量 m

	#递归处理每一个mov，并将对应的trp和dat上传到服务器
	for root,dirs,files in os.walk(dir):
		for file in files:
			file = file.lower()
			b,ext = os.path.splitext(file)

			if ext.lower() not in ('.mov',):
				continue

#			trp = os.path.join(root,b+'.trp')
#			if not os.path.exists(trp):
#				continue

			mov = os.path.join(root,file)
			mov = os.path.normpath(mov)
			needspace = os.path.getsize(mov)
			print 'show:',needspace,mov
			#申请一个nodeserver
			server = conf['ctrlserver']

			node = applyNodeServer(needspace,server)
			if not node:
				print 'no NodeSpace available!'
				return False
#			print node
			sync = ImageSyncronizer()
			rc =   sync.send(node,mov)
			print rc
			if not rc:
				return False
#			return


class ImportMany():
	def __init__(self):
		self.driveList = []
		self.movlist = []
		self.queryDevice()
		self.queryFlag()
		self.joinDev()

	def queryDevice(self):
		self.driveList = []
		drivelist = win32api.GetLogicalDriveStrings().replace('\x00',',')[:-1].split(',')
		for path in drivelist:
			if kernel32.GetDriveTypeA(path) == win32con.DRIVE_REMOVABLE:
				self.driveList.append(path)
				#self.form.com_path.addItem(path)
		if not(len(self.driveList)):
			print "Can't find anyone drive!"
			return 0

	def queryFlag(self):
		for dev in self.driveList:
			statFlag = os.path.join(dev,'import.success')
			if os.path.exists(statFlag):
				self.driveList.remove(dev)

	def joinDev(self):
		for dev in self.driveList:
			for root,dirs,files in os.walk(dev):
				if os.path.basename(root) == 'DCIM' and '100MEDIA' in dirs:
					path = os.path.join(root)
					self.movlist.append(path)

if __name__=='__main__':
	copyNow = ImportMany()
	movCount = len(copyNow.movlist)
	nowCount = 1
	runtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	applog = os.path.join(os.getcwd(),'runtime_%s.log' %runtime)
	open_applog = open(applog,'w')
	for movpath in copyNow.movlist:
		print '当前处理进度：%s/%s,当前路径为%s'.decode('utf-8') %(nowCount,movCount,movpath)
		gs600_trp_2.do_convert(movpath)
		if syncDir(movpath) == False:
			open_applog.write('[*] %s %s Error' %(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),movpath))
		dev = movpath.split('\\')
		successfile = os.path.join(dev[0] + '\\','import.success')
		openlog = open(successfile,'w')
		openlog.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		openlog.close()
		nowCount += 1
	open_applog.close()
	main_pause = raw_input('successfully,press enter for exit'.decode('utf-8'))

	'''
	dir = 'S:/test_data/1-2/DCIM/100MEDIA'
	args = sys.argv[1:]
	if len(args) < 2 :
		print 'invalid command! \n sto_syncer convert|import MEDIAFILE_DIR'
		sys.exit()
	if args[0] =='convert':
		#转换trp
		gs600_trp_2.do_convert(args[1])
		sys.exit()
	if args[0] == 'import':
		syncDir(args[1])
		sys.exit()

	#syncDir(sys.argv[1])
	'''
	