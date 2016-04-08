# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading
import ffmpeg

app = QtGui.QApplication(sys.argv)

import ctypes
from ctypes import *



mtx = threading.Lock()
frames =[]


ffmpeg.InitLib()
#fc =  ffmpeg.InitAvFormatContext('d:/movies/marieMcCray.avi')
fc =  ffmpeg.InitAvFormatContext('D:/test_dvr_data/stosync/a.wmv')
#fc =  ffmpeg.InitAvFormatContext('D:/file0014.mov')

bytes=0
codec = ffmpeg.InitAvCodec(fc.contents.video)


vi = ffmpeg.MediaStreamInfo_t()		
vi.codec_type = 0
vi.codec_id = 17
vi.width = 1920
vi.height =1080
vi.gopsize = 12
vi.pixfmt = 0
vi.tb_num =1
vi.tb_den = 1000
vi.bitrate = 0
vi.frame_number =0
vi.videostream = 0

codec = ffmpeg.InitAvCodec(vi)
		

class LazyDisplayQt(QtGui.QMainWindow):    
	def __init__(self, *args):
		QtGui.QMainWindow.__init__(self, *args)        
		self.timer = QtCore.QTimer(self)        
		self.timer.setInterval(10)
		self.connect(self.timer,SIGNAL("timeout()"),
					 self.on_timer_timeout)
		#ffmpeg.SeekToTime(fc,90)
		self.timer.start()
		self.show()
		
	def __del__(self):
		self.hide()

	def on_timer_timeout(self):
		#print 'timer event..'
		cnt=0
		if True:
			pkt = ffmpeg.ReadNextPacket(fc)
			if not pkt:return
			
			pkt2 = ffmpeg.AllocPacket()			
			pkt2.contents.data = create_string_buffer(pkt.contents.data[:pkt.contents.size])			
			pkt2.contents.size = pkt.contents.size
			
			pkt2.contents.stream = 0
			#print pkt2.contents.size
			frame = None
		
			frame = ffmpeg.DecodeVideoFrame(codec,pkt2)
			
			
			ffmpeg.FreePacket(pkt2,1)
			
			
			if frame:
				mtx.acquire()
				frames.append(frame.contents)
				mtx.release()        
				#ffmpeg.FreeVideoFrame(frame) #memory leak    
			
			ffmpeg.FreePacket(pkt,1)
		self.repaint()
		
	def paintEvent(self, ev):        
		f = None
		mtx.acquire()
		if len(frames):
			f = frames[0]
			del frames[0]        
		#print len(frames)
		mtx.release()
		if not f:
			return 
		
		self.p = QtGui.QPainter()
		self.p.begin(self)
		data = f.rgb24[:f.size]
		
		image = QImage(data,f.width,f.height,QImage.Format_RGB888)
		self.p.drawImage(QtCore.QRect(0,0,self.width(),self.height()),
						 image,
						 QtCore.QRect(0,0,f.width,f.height))
		self.p.end()
		ffmpeg.FreeVideoFrame(f)


ld=LazyDisplayQt()

app.exec_()
