# -- coding:utf-8 --

import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,json,zlib

import message
from message import *
import network
from network import * 
from msg_imgplay import * 

import utils

from errbase import *
import ffmpeg



#播放视频状态
class VideoState:
	def __init__(self):
		self.ctx = None #解码上下文
		self.session = None #播放会话
		self.status = 0  #0 - stopped, 1 - playing ,2 - paused, 3 - exited 
		self.thread = None
		self.conn = None
		self.mtx = threading.Lock()
		self.sequence = 0
		
		
class MediaServer(NetService):
	def __init__(self,name,addr):
		NetService.__init__(self,name,addr)
		self.tmpdir='.'
		self.conf = None
		#self.app = app
		ffmpeg.InitLib()
	
	def init(self,conf): # conf - json
		pass
		
	def setTempFileDir(self,path):
		'''设置临时文件存放目录'''
		pass
		
	def run(self,wait=False):
		pass
		
	def shutdown(self):
		pass
	
	def dispatchMsg(self,m,conn):
		msg = m.getMsg()
		print msg
		if msg== 'imageplay_init':
			session = m.attrs
			session['conn'] = conn
			conn.delta = session
			self.eventImagePlayInit(session)
			return 
		
		if msg == 'imageplay_start':
			session = conn.delta
			self.eventImagePlayStart(session)
			return 
		
		if msg == 'imageput_end':
			session = conn.delta
			self.eventImagePlayEnd(session)
			return
		
		if msg == 'imageplay_pause':
			session = conn.delta
			self.eventImagePlayPause(session)
			return 
		
		if msg =='imageplay_seek':
			session = conn.delta
			timesec = m.attrs['time']
			session['sequence'] = m.attrs['sequence']
			self.eventImageSeek(timesec,session)
			
	def eventImageSeek(self,timesec,session):
		session['vs'].mtx.acquire()
		try:
			print 'seek time:',timesec,type(timesec)
			session['vs'].sequence+=1		
			ffmpeg.SeekToTime(session['vs'].ctx,int(timesec) )
			print 'seek time to ',timesec		
		except:
			traceback.print_exc()
	
		session['vs'].mtx.release()
		
	def eventImagePlayPause(self,session):
		session['vs'].status = 2
		
	def eventImagePlayStart(self,session):
		session['vs'].status = 1
		
	
		
	def eventImagePlayEnd(self,session):
		session['vs'].status = 0
		session['vs'].sequence+=1
		
	def eventGotMessage(self,msglist,conn):
		
		for m in msglist:
			self.dispatchMsg(m,conn)
	
	def eventConnCreated(self,conn):		
		NetService.eventConnCreated(self,conn)
		thread = NetConnThread(conn)
	
	def eventConnDisconnected(self,conn):		
		NetService.eventConnDisconnected(self,conn)
		session = conn.delta
		vs = session['vs']
		vs.status = 3 #准备退出
	
	def getImageFile(self,imageuri):
		pass #shold be overrided

	
	def eventImagePlayInit(self,session):
		conn = session['conn']
		uri = session['imageid'] #影像编号
		#从索引库中检索到影像文件
		file =self.getImageFile(uri)
		print 'GeiImageFile:',file
		if not file:
			conn.sendMessage(MsgCallReturn(False))
			conn.close()
			return
		mt = utils.getmtime(file)
		if mt ==0:
			print 'get modifytime failed!(%s)'%file
			conn.sendMessage(MsgCallReturn(False))
			conn.close()
			return
		filesize = os.path.getsize(file)
		if filesize==0:
			print 'get filesize failed!(%s)'%file
			conn.sendMessage(MsgCallReturn(False))
			conn.close()
			return
		
		
		session['file'] = file 
		#通过解码库获取image信息，返回到客户端
		# init AvformatCtx
		
		ctx = ffmpeg.InitAvFormatContext(session['file'])
		if not ctx:
			print 'Init AvForm Failed...'
			conn.sendMessage(MsgCallReturn(False,errmsg=u'Open ImageFile Failed!'))
			conn.close()
			return 
		vs = VideoState()
		vs.ctx = ctx
		session['vs'] = vs
		vs.session = session
		
		m = MsgImagePlay_Profile()
		duration = vs.ctx.contents.video.duration
		m.attrs['duration'] = duration
		m.attrs['filesize'] = filesize
		m.attrs['createtime'] = mt - duration
		m.attrs['videoctx'] =  self.hashStreamContext(vs.ctx.contents.video) #视频解码上下文
		m.attrs['audioctx'] = None
		r = conn.sendMessage(m)
		if not r:
			conn.close()
			return 
		#启动发送线程
		print 'image start time:',m.attrs['createtime'],'time-len:',duration
		print 'lauch send thread..'
		vs.thread = threading.Thread(target=self.threadVideoSend,args=(vs,))
		vs.conn = conn
		vs.thread.start()
		
	def hashStreamContext(self,ctx):
		h = {'codec_type':ctx.codec_type,
			'codec_id':ctx.codec_id,
			'width':ctx.width,
			'height':ctx.height,
			'gopsize':ctx.gopsize,
			'pixfmt':ctx.pixfmt,
			'tb_num':ctx.tb_num,
			'tb_den':ctx.tb_den,
			'bitrate':ctx.bitrate,
			'frame_number':ctx.frame_number,
			'videostream':ctx.videostream,
			'duration':int(ctx.duration/1000000)
		}
		return h
		
	#影像读取发送线程
	def threadVideoSend(self,vs):
		'''
			发送数据如果对方接收慢，则会阻塞起来,阻塞住的话如果客户端进行跳跃就会存在问题
			发送失败表示连接断开
			读到文件尾部表示视频结束,如果sequence
			 0 - stopped, 1 - playing ,2 - paused, 3 - exited 
		'''
		#vs.status = True
		print 'threadVideoSend...'
		cnt=0
		while True:
			if vs.status in (3,) :
				break #结束,退出线程 
			if vs.status !=  1:
				time.sleep(0.005)
				continue
				
			vs.mtx.acquire()	
			pkt = ffmpeg.ReadNextPacket(vs.ctx)
			if not pkt: #读到文件尾部了
				vs.status = 3
				#ffmpeg.SeekToTime(vs.ctx,0) #移动到文件头
				vs.mtx.release()
				print 'read reach end..'
				vs.conn.close()
				continue
			vs.mtx.release()
			#发送包
			m = MsgImagePlay_Packet()
			m.bin = pkt.contents.data[:pkt.contents.size]
			m.attrs['sequence'] = vs.sequence
			m.attrs['stream'] = vs.ctx.contents.video.videostream
			m.attrs['count'] = cnt
			m.attrs['duration'] = pkt.contents.duration
			cnt+=1
			#print 'count:',cnt
			#time.sleep(0.2)
			#print 'send bytes:',pkt.contents.size
			r = vs.conn.sendMessage(m)
			ffmpeg.FreePacket(pkt,1)
			if not r:
				vs.status = 3				
		
		ffmpeg.FreeAvFormatContext(vs.ctx)
		print 'Video Read thread exit...'
	
#MediaPlayclient 
#播放客户端基础类
desc='''
	客户端连接服务器，提交播放请求，接收packet即可解码获取视频帧，将frame置入队列，设置最大frame缓冲数量,接收超过缓冲数量则阻塞接收packet
	每次接收到packet都具有一个sequence(用于控制缓存丢弃),一旦发现packet改变，将丢弃缓冲队列中所有的frame
	每请求一次视频则创建一次连接，并启动一个线程
'''
class MediaPlayClient:
	def __init__(self):
		
		self.recvmsg=[] #接收到的消息
		self.mtx_recvmsg=threading.Condition()
		self.session = None #视频播放会话
		self.frames =[]
		self.maxcachedsecs = 0 #缓存最大秒数的视频
		self.maxcachedframes = 0 #最大缓存帧数
		self.mtxframe = threading.Condition()
		self.status = 0
		self.waitobj = utils.MutexObject()
		self.curconn = None #当前播放链接
	
	def getPlaySession(self):
		return self.session
	

	def playReset(self):
		self.curconn = None
		
	def playConnect(self,server,imageuri):
		'''
			server - (addr,port)
			imageuir - (node.hashid)
		'''
		self.playReset()
		
		conn = NetConnection(recvfunc = self.recvEvent)		
		addr = server
		r = conn.connect( addr)
		if r == False:
			return NETMSG_ERROR_DESTHOST_UNREACHABLE
		
		m = MsgImagePlay_Init(imageuri)
		m.attrs['imageid'] = imageuri
		m.attrs['sequence'] = 0
		
		r = conn.sendMessage(m)
		
		if not r:
			return NETMSG_ERROR_SENDDATA_FAILED
		
		session=m.attrs
		conn.delta = session
		session['conn'] = conn
		self.session = session
		thread = NetConnThread(conn)
		#准备接收profile
		m = self.waitobj.waitObject(5)
		
		
		if not m: #超时没有返回，错误处理
			print 'server response timeout!'
			conn.close()
			return NETMSG_ERROR_RESPONSE_TIMEOUT #超时
		if m.getMsg()!='imageplay_profile':
			conn.close()
			return NETMSG_ERROR_INVALID_MSG
		
		self.curconn = conn
		
		profile = m.attrs # 视频描述信息
		#初始化解码器
		print profile
		#将profile.videoctx转换为ffmpeg.VideoStreamInfo
		vctx = profile['videoctx']
		vi = ffmpeg.MediaStreamInfo_t()		
		vi.codec_type = vctx['codec_type']
		vi.codec_id = vctx['codec_id']
		vi.width = vctx['width']
		vi.height = vctx['height']
		vi.gopsize = vctx['gopsize']
		vi.pixfmt = vctx['pixfmt']
		vi.tb_num = vctx['tb_num']
		vi.tb_den = vctx['tb_den']
		vi.bitrate = vctx['bitrate']
		vi.frame_number = vctx['frame_number']
		vi.videostream = vctx['videostream'] # stream index
		
		vcodec = ffmpeg.InitAvCodec(vi) #初始化解码器
		
		session['vcodec'] = vcodec
		session['profile'] = profile
		
		if vcodec ==None:
			
			conn.close()
			return Error_AllocCodec_Failed
		
		self.setMaxCachedTimeSeconds(10) #最大10秒钟缓冲
		
		return ERROR_SUCC
		
	#	#1.发送put_init
	#def getMessage(self,lock=False):
	#	m = None
	#	if lock:self.mtx_recvmsg.acquire()
	#	
	#	if len(self.recvmsg):
	#		m = self.recvmsg[0]
	#		del self.recvmsg[0]
	#	if lock:self.mtx_recvmsg.release()
	#	
	#	return m
	#
	#def getMessageTimeout(self,timeout = 5):
	#	#等待第一个包返回 
	#	self.mtx_recvmsg.acquire()
	#	m = self.getMessage()
	#	if not m:
	#		self.mtx_recv.wait(timeout) #等待5秒钟如果没有返回则
	#	m = self.getMessage()
	#	self.mtx_recvmsg.release()
	#	return m
	
	def clearVideoFrames(self,lock=True):
		if lock: self.mtxframe.acquire()
		for f  in self.frames:
			self.freeVideoFrame(f)
		self.frames = []
		
		if lock: self.mtxframe.release()
	
		
	#获取视频帧,快速获取
	def getVideoFrame(self):
		f = None
		self.mtxframe.acquire()
		if self.frames:
			f = self.frames[0]
			del self.frames[0]		
		self.mtxframe.release()
		return f
		
	def freeVideoFrame(self,frame):
		ffmpeg.FreeVideoFrame(frame)
		
	#获取视频播放帧率
	def getVideoFps(self):
		fps = 0
		if self.session:
			vctx = self.session['profile']['videoctx']
			num = vctx['tb_num']
			den = vctx['tb_den']
			fps = int( 1/(num/float(den)) )
		return fps
	
	def setMaxCachedTimeSeconds(self,secs):
		self.maxcachedsecs = secs
		self.maxcachedframes = secs * self.getVideoFps()
			
	
		
	#播放结束server发送end到次
	def dispatchMsg(self,m,conn):		
		if m.getMsg() == 'imageplay_data':
			session = conn.delta		
			self.eventRecvStreamPacket(m,session)			
			return 
		
		#if m.getMsg() =='imageplay_end':
		#	session = conn.delta
		#	self.eventStreamEnd(m,session)
		self.waitobj.notify(m)
		
		
		#self.mtx_recvmsg.acquire()
		#self.recvmsg.append((m,conn))
		#self.mtx_recvmsg.notify()
		#self.mtx_recvmsg.release()
	
	 
	
	def recvEvent(self,evt):		
		if evt.type == NetConnectionEvent.EVENT_DATA:
			for m in evt.data:
				self.dispatchMsg(m,evt.conn)
		if evt.type == NetConnectionEvent.EVENT_DISCONNECTED:
			print 'connection lost!'
			self.eventConnDisconnected(evt.conn)
	
	#连接断开了，清除工作
	def eventConnDisconnected(self,conn):
		session = conn.delta
		vcodec = session['vcodec']
		self.status = 3 # exited
		if vcodec:
			ffmpeg.FreeAvCodec(vcodec)
		
	def playStart(self):
		try:
			conn = self.session['conn']
			m = MsgImagePlay_Start()
			conn.sendMessage(m)
		except:pass
		
	
	def playPause(self):
		try:
			conn = self.session['conn']
			m = MsgImagePlay_Pause()
			conn.sendMessage(m)
		except:pass
	
	def playResume(self):
		try:
			conn = self.session['conn']
			m = MsgImagePlay_Resume()
			conn.sendMessage(m)
		except:pass
	
	def playEnd(self):
		try:
			conn = self.session['conn']
			conn.close()
			#m = MsgImagePlay_End()
			#conn.sendMessage(m)
		except:pass
	
	def playSeek(self,secs):
		try:
			conn = self.session['conn']
			self.session['sequence'] += 1
			seq =  self.session['sequence']
			m = MsgImagePlay_Seek(secs,seq)
			conn.sendMessage(m)
		except:
			traceback.print_exc()
			
		
def global_inits():
	ffmpeg.InitLib()
	
def global_cleanup():
	ffmpeg.Cleanup()

if __name__=='__main__':
	pass
	