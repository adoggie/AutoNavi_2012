# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,threading,traceback,os
import ffmpeg
import imgbase

class ImagePlayWindow(QFrame):    
	def __init__(self,console,app):
		QFrame.__init__(self)
		self.app = app
		self.console = console
		self.timer = QTimer(self)
		self.connect(self.timer,SIGNAL("timeout()"),
					self.on_timer_timeout)
		#
		self.w = 600
		self.h = 400
		self.paused = False
		self.lastframe = None

		self.bgimage=None

		self.resize(self.w,self.h)
		self.setWindowTitle(u'视频窗口')

		self.initUi()
		self.show()
		self.timer.start(5)



	def initUi(self):
		try:
			img = QImage()

			img.load('bgdemo.jpg')
			if img:
				self.bgimage =img
		except:
			traceback.print_exc()
			sys.exit(0)

	def setFps(self,fps):
		self.timer.stop()
		self.timer.start( int(1000/fps) )

	def __del__(self):
		self.hide()

	def on_timer_timeout(self):
		self.repaint()
		self.console.raise_()

	def setPaused(self,pause):
		self.paused = pause

	def resizeEvent(self,ev):
		self.w = ev.size().width()
		self.h = ev.size().height()

	def getLastFrame(self):
		return self.lastframe

	def drawFrame(self,f):
		f = f.contents
		self.p = QtGui.QPainter()
		self.p.begin(self)
		data = f.rgb24[:f.size]
		image = QImage(data,f.width,f.height,QImage.Format_RGB888)
		self.p.drawImage(QtCore.QRect(0,0,self.width(),self.height()),
						 image,
						 QtCore.QRect(0,0,f.width,f.height))
		self.p.end()
		#self.console.freeVideoFrame(frame)

	def drawDefault(self,ev):
		#QFrame.paintEvent(self,ev)
		image = self.bgimage
		if not image:
			return
		self.p = QtGui.QPainter()
		self.p.begin(self)

		self.p.drawImage(QtCore.QRect(0,0,self.width(),self.height()),
						 image,
						 QtCore.QRect(0,0,image.size().width(),image.size().height()))
		self.p.end()


	def paintEvent(self, ev):

		if self.paused:
			if self.lastframe:
				self.drawFrame(self.lastframe)
			return

		frame = self.console.getVideoFrame()
		if not frame:
			if self.lastframe:
				self.drawFrame(self.lastframe)
			else:
				self.drawDefault(ev)
			return
		if self.lastframe:
			self.console.freeVideoFrame(self.lastframe)
		self.lastframe = frame
		self.drawFrame(self.lastframe)

		#self.p = QtGui.QPainter()
		#self.p.begin(self)
		#f = frame.contents
		#data = f.rgb24[:f.size]
		#image = QImage(data,f.width,f.height,QImage.Format_RGB888)
		#self.p.drawImage(QtCore.QRect(0,0,self.width(),self.height()),
		#                 image,
		#                 QtCore.QRect(0,0,f.width,f.height))
		#self.p.end()
		#self.console.freeVideoFrame(frame)

		ev.accept()





	def startPlay(self):
		self.show()
		try:
			s = self.app.getPlaySession()
			vsi = s['profile']['videoctx']
			w,h = vsi['width'],vsi['height']
			self.resize(w,h)
			self.w = w
			self.h = h
		except:
			traceback.print_exc()

	def zoomIn(self): #放大
		#QMessageBox.about(self,"abc",'xxx')
		#print self.w,self.h
		self.w*=1.5
		self.h*=1.5
		self.resize(self.w,self.h)
		#print self.w,self.h

	def zoomOut(self): #缩小
		self.w/=1.5
		self.h/=1.5
		self.resize(self.w,self.h)
		#print self.w,self.h

	def stopPlay(self):
		try:
			self.lastframe = None

		except:pass


	def mousePressEvent(self,evt):

		evt.accept()
		self.console.doPlay()