# -*- coding: utf-8 -*-
# playconsole.py
# 播放控制台

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ctypes
from ctypes import *

import sys,threading,time,datetime,traceback,json
from  ui_playconsole import *
from msg_plugin import *
from mediasvr import *
import ffmpeg

from playwindow import *

PLAY_STOPPED = 0
PLAY_PLAYING = 1
PLAY_PAUSED  = 2

'''
problems:
=================
1. qt button触发事件采用 on_btnZoomOut_clicked()方式定义时间slot发现被触发2次
   但采用 self.connect()之后便无此问题


创建一个定时器，用于定时读取playduration,定位到gps坐标，并送到地图展示

'''

class PlayStat:
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.timelen= 0	#播放时长
		self.timestart = 0	#开始时间
		self.timeduration = 0 	#当前播放偏移时间
		self.sequence = 0
		self.filesize = 0 #媒体文件长度
		self.lastduration = 0

		self.lat = 0
		self.lon = 0
		self.gpstime = 0
		self.imageid=0
		
class PlayProfile:
	def __init__(self):
		self.image_uri=''
		self.server=()
		
		
class PlayConsoleWindow(QtGui.QFrame,Ui_ConsoleWnd,MediaPlayClient):    
	def __init__(self,app):
		QtGui.QFrame.__init__(self)
		MediaPlayClient.__init__(self)
		self.setupUi(self)
		
		self.playwnd = ImagePlayWindow(self,app)
		self.app = app
		self.show()
		self.status = PLAY_STOPPED # 0 - stopped, 1 - playing ,2 - pausing
		
		
		self.playduration = 0 #播放进度 secs
		self.timer = QTimer(self)        
		self.connect(self.timer,SIGNAL("timeout()"),self.onTimerDuration)
		self.timer.start(1000)
		
		self.connect(self.btnZoomIn,SIGNAL('clicked()'),self.btnZoomIn_clicked)
		self.connect(self.btnZoomOut,SIGNAL('clicked()'),self.btnZoomOut_clicked)
		self.connect(self.btnPlay,SIGNAL('clicked()'),self.btnPlay_clicked)
		self.connect(self.btnStop,SIGNAL('clicked()'),self.btnStop_clicked)
		self.connect(self.btnCaptureScreen,SIGNAL('clicked()'),self.btnCaptureScreen_clicked)
		
		
		#self.connect(self.sliderTimeLine,SIGNAL('sliderReleased()'),self.slider_sliderReleased)
		#self.connect(self.sliderTimeLine,SIGNAL('sliderMoved(int)'),self.slider_sliderMoved)
		

		self.profile={'id':0}
		self.playstat = PlayStat()
		
		server = self.app.conf.get('nodeserver',('localhost',12004))
		#self.setPlayProfile({'image_uri':'abc','server':server})

#	获取视频播放窗口
	def getPlayWnd(self):
		return self.playwnd

	def showWindow(self,b=True):
		if b:
			self.show()
			self.getPlayWnd().show()
		else:
			self.hide()
			self.getPlayWnd().hide()


	def getPlayProfile(self):
		return self.profile

	def seekTime(self,gpstick):
		try:
			offsec = gpstick - self.playstat.timestart
			self.playSeek(offsec)
		except:
			traceback.print_exc()
			
	def __del__(self):
		self.hide()



	def slider_sliderMoved(self,value):
		print 'slider moved'
		
	def slider_sliderReleased(self):
		print 'slider:',self.sliderTimeLine.value()
	
	
	def btnCaptureScreen_clicked(self):
		try:
#			self.getImageTagInfo()
#			return

			tt =self.playstat.timestart + self.playstat.timeduration
			name = utils.formatTimestamp(tt)
			
			f = self.playwnd.getLastFrame()
			f = f.contents			
			data = f.rgb24[:f.size]
			image = QImage(data,f.width,f.height,QImage.Format_RGB888)
			image.save("%s.jpg"%(name.replace(':','-')) )
			print name
		except:
			traceback.print_exc()

#	获取当前播放的标记信息
	def getImageTagInfo(self,fmt='JPG'):
		try:
			if not self.isPlaying():
				return None

			f = self.playwnd.getLastFrame()
			f = f.contents
			data = f.rgb24[:f.size]
			image = QImage(data,f.width,f.height,QImage.Format_RGB888)
			bf = QBuffer()
			image.save(bf,fmt,75)
#			ff = open('c:/test.jpg','wb')
#			ff.write(bf.data().data())
#			ff.close()
#			return None

			r ={
				'digest':self.getPlayProfile()['image_uri'],
				'imageid': self.getPlayProfile()['id'],
				'time':self.playstat.gpstime,
				'lon':self.playstat.lon,
				'lat':self.playstat.lat,
				'width':f.width,
				'height':f.height,
				'image':bf.data().data()}
			return r
		except:
			traceback.print_exc()
			return None

	def btnZoomIn_clicked(self):
		self.playwnd.zoomIn()
		
	def btnZoomOut_clicked(self):
		self.playwnd.zoomOut()
		
	def btnPlay_clicked(self):
		self.doPlay()
	
	def btnStop_clicked(self):
		self.doStop()
		
	def doPlay(self):
		self.playwnd.setPaused(False)
		
		if self.status == PLAY_STOPPED:
			print 'doPlay:',self.profile['server'],self.profile['image_uri']
			r = self.playConnect( self.profile['server'],self.profile['image_uri'])
			if r!=ERROR_SUCC:
				#print '连接到服务器:%s 失败!'%self.profile['server']
				QMessageBox.about(self,'Error','connect to server:%s failed!'% str(self.profile['server']))
				self.status = PLAY_STOPPED
				return
			self.playStart()
			#self.timer.start(1000)
			self.status = PLAY_PLAYING
			self.setUiText()
			self.onPlayStart()
			
				
			return
		
		if self.status == PLAY_PAUSED:
			self.playStart()
			self.status = PLAY_PLAYING
			self.setUiText()
			
			return
		
		if self.status == PLAY_PLAYING:
			self.playPause()
			self.status = PLAY_PAUSED
			self.setUiText()
			self.playwnd.setPaused(True)
			return

	def doPause(self):
		if self.status == PLAY_PLAYING:
			self.playPause()
			self.status = PLAY_PAUSED
			self.setUiText()
			self.playwnd.setPaused(True)


	#视频开始播放
	def onPlayStart(self):
		try:
			vctx =self.session['profile']['videoctx']			
			w = vctx['width']/3
			h = vctx['height']/3
			
			self.playwnd.resize(w,h)
			self.playstat.timelen = self.session['profile']['duration'] #时长
			self.playstat.timestart = self.session['profile']['createtime'] #开始时间
			self.sliderTimeLine.setRange(0,self.playstat.timelen)
			self.sliderTimeLine.setPageStep(self.playstat.timelen/10)
			self.playstat.lastduration = 0
			desc ="w,h:%s x %s ids:%s"%(vctx['width'],vctx['height'],self.session['imageid'])
			self.txtImageDesc.setText(desc)
			print 'onPlayStat: timestart:',self.playstat.timestart,'time-length:',self.playstat.timelen
			
			
		except:
			traceback.print_exc()
			
	def setUiText(self):
		if self.status == PLAY_PAUSED:
			self.btnPlay.setText(u'播放')
		if self.status == PLAY_STOPPED:
			self.btnPlay.setText(u'播放')
		if self.status == PLAY_PLAYING:
			self.btnPlay.setText(u'暂停')
		
	def onReset(self):
		self.setUiText()
		self.sliderTimeLine.setValue(0)
	
	def doStop(self):
		try:
			self.btnPlay.setText(u'播放')
			self.status = PLAY_STOPPED
			self.playEnd()
			self.session['conn'].close()
			
			self.playwnd.setPaused(False)
			self.playwnd.stopPlay()
		except:
			pass


	def closeEvent(self,evt):
		self.doStop()
		QWidget.closeEvent(self,evt)
		self.playwnd.hide()

	def setPlayProfile(self,profile):
		'''
			profile - {'id','image_uri','server':(host,port),'gpsdata':None,'duration','startime'}
			image_uri - 文件的digest
			duration - 时长 seconds
			startime - 开始时间 seconds 
			gpsdata - 从数据库中获取的连续的轨迹信息,默认是json编码的字符串
		'''
		gpsdata = profile['gpsdata']
		gpsdata = json.loads(gpsdata)
		profile['gpsdata'] =  gpsdata		
		print  'json load gpsdata succed!','*'*20
			
		self.profile = profile
	
	def isPlaying(self):
		return self.status != PLAY_STOPPED	
	
	def eventConnDisconnected(self,conn):
		try:
			print 'play disconnected..'
			vcodec = self.session['vcodec']
			ffmpeg.FreeAvCodec(vcodec)
			self.session = None
			self.status = PLAY_STOPPED
			#self.timer.stop()
			self.onReset()
			self.clearVideoFrames()
			
		except:traceback.print_exc()

	
	def eventRecvStreamPacket(self,m,session):
		seq = session['sequence']		
		if m.attrs['sequence'] != seq: #新的播放序列开始，清除缓存帧
			self.clearVideoFrames()
			return 
			#session['sequence'] = m.attrs['sequence']
		#解码开始
		frame = None
		pkt = ffmpeg.AllocPacket()
		
		pkt.contents.data = create_string_buffer(m.bin[:len(m.bin)])
		pkt.contents.size = len(m.bin)
		pkt.contents.sequence = m.attrs['sequence']
		pkt.contents.duration = m.attrs['duration']
		pkt.contents.stream = m.attrs['stream']
		
		#print "net pakcet duration:",pkt.contents.duration
		
		vcodec = session['vcodec']
		#print m.attrs['count']
		#time.sleep(0.2)
		 
		frame = ffmpeg.DecodeVideoFrame(vcodec,pkt)		
		#
		#print 'frame duration:',frame.contents.duration
		ffmpeg.FreePacket(pkt,0)
		if frame: #依据缓冲frame数量控制接收
			if frame.contents.duration != self.playduration:
				self.playduration = frame.contents.duration
				#self.app.playDurationChanged(self.playduration,self.profile) #
			while True:
				if self.status == PLAY_STOPPED: # exited
					self.clearVideoFrames()
					return 
				self.mtxframe.acquire()
				#print 'cached frames:',self.maxcachedframes,len(self.frames)
				if len(self.frames) < 10:#self.maxcachedframes:
					self.frames.append(frame)			
					self.mtxframe.release()
					break
				#print 'frame overload:%s',len(self.frames)
				self.mtxframe.release()
				
				time.sleep(0.05) #frame溢出了，等等接收
	
	def getVideoFrame(self):
		f = MediaPlayClient.getVideoFrame(self)
		if f:
			try:
				self.playstat.timeduration = f.contents.duration
				self.playstat.sequence = f.contents.sequence				
			except:pass
		return f
	
	def onTimerDuration(self):
#		print 'on Timer..'
		if self.status == PLAY_STOPPED:
			#self.timer.stop()
			self.onReset()
			return
		try:
			#print self.playstat.timeduration
			off = self.sliderTimeLine.value() - self.playstat.lastduration
			#print self.playstat.lastduration
			if abs(off) >=5:
				print 'seek:',self.sliderTimeLine.value(),self.playstat.timeduration
				self.playSeek(self.sliderTimeLine.value())
				self.clearVideoFrames()
				time.sleep(0.02) #有包收上来了单还没进入缓冲队列
				self.clearVideoFrames()				
				#self.playstat.timeduration =self.sliderTimeLine.value()	
				#self.clearVideoFrames() #虽然可以清除本地包缓冲，但tcp缓冲内还有尚未处理的消息包
			else:
				self.sliderTimeLine.setValue(self.playstat.timeduration)
			
			self.playstat.lastduration = self.sliderTimeLine.value()
			
			
			m1,s1  =self.playstat.timeduration//60,self.playstat.timeduration%60
			m2,s2  =self.playstat.timelen//60,self.playstat.timelen%60			
			txt ="[ %02d:%02d / %02d:%02d]"%(m1,s1,m2,s2)			
			self.txtTime1.setText(txt)
			
			s = self.playstat.timestart
			e = s + self.playstat.timelen
			txt = "[ %s - %s ]"%(utils.formatTimestamp(s),utils.formatTimestamp(e))
			self.txtTime2.setText(txt)



#			print "#1."
			gpsdata = self.profile.get('gpsdata',None)
			if  gpsdata== None:
				return
#			print "#2."
			#duration seek to gps time
			gpstime = self.playstat.timestart + self.playstat.timeduration
			self.playstat.gpstime = gpstime

#			print "#3."
			for pt in gpsdata:				
				tick = int(pt['time'])
#				print tick,gpstime
				if tick >= gpstime:
					print "#4."
					#回调到内业软件显示车辆坐标
					m = MsgPlugin_ShowSymbol_2()
					m['pos'] = pt #
					self.playstat.lon = pt['lon']
					self.playstat.lat = pt['lat']

					self.app.getPluginService().sendMessage(m)
					#print 'gps postion recalled..',pt
					break
			#2. 显示播放进度
		except:
			traceback.print_exc()
		
		


if __name__=='__main__':
	app = QtGui.QApplication(sys.argv)
	ld=PlayConsoleWindow()
	app.exec_()
