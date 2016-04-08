#	--	coding:utf-8	--

import	traceback,os,os.path,sys,time,ctypes

import	ffmpeg
import	ctypes
from	ctypes	import	*

def	printStreamInfo(s):
	print	s.codec_type,'codec_id:',s.codec_id,\
		'width:',s.width,'height:',s.height,\
		'gopsize:',s.gopsize,'pixfmt:',s.pixfmt,\
		'timebase_num:',s.tb_num,'timebase_den:',s.tb_den,\
		'bitrate:',s.bitrate,'framenumber:',s.frame_number,\
		'streamindex:',s.videostream,'extrsize',s.extrsize,s.extr[:s.extrsize]

def	printFrameInfo(f):
	print	len(f.rgb24[:f.size]),'width:',f.width,'height:',f.height,'duration:',f.duration,'size:',f.size
	

def	saveppm(f,file):
	fp	=	open(file,'wb')
	if	not	fp:
		return
	fp.write(	"P6\n%d	%d\n255\n"%(f.width,f.height)	)
	fp.write(f.rgb24[:f.size])
	fp.close()
	print	file
		
	
ffmpeg.InitLib()
fc	=	ffmpeg.InitAvFormatContext('d:/FILE0020.MOV')
#fc	=	ffmpeg.InitAvFormatContext('d:/movies/MarieMcCray.avi')



printStreamInfo(fc.contents.video)
#sys.exit()


bytes=0
codec	=	ffmpeg.InitAvCodec(fc.contents.video)
#print	codec	#apply	a	codec
#ffmpeg.FreeAvCodec(codec)
#sys.exit()

#print	type(	create_string_buffer	('abc'))
#b=create_string_buffer('sdfdsdsf')
#x	=ctypes.cast(ctypes.byref(b),	ctypes.POINTER(ctypes.c_char))
#print	type(x)

cnt=0

ffmpeg.SeekToTime(fc,100)
while	True:
	pkt	=	ffmpeg.ReadNextPacket(fc)
	if	not	pkt:
		print 'read pkt is null'
		break
	bytes	+=	pkt.contents.size
	
	#print	type(pkt.contents.data)
	
	#pkt	=	ffmpeg.AllocPacket()
	#d	=	'100'*2045
	#pkt.contents.data.contents	=	pointer(	d)
	#pkt.contents.size	=	len(d)
	#	
	
	frame	=	ffmpeg.DecodeVideoFrame(codec,pkt)
	if	frame:
		cnt+=1
		printFrameInfo(frame.contents)
		if	cnt	<	100:
			saveppm(frame.contents,"d:/temp5/%s_xx.ppm"%cnt)
			os.system('convertx	%s	%s'%("d:/temp5/%s_xx.ppm"%cnt,"d:/temp5/%s_xx.jpg"%cnt))
		ffmpeg.FreeVideoFrame(frame)	#memory	leak
		print	pkt.contents.stream,pkt.contents.size,pkt.contents.duration
		break
	#print	pkt.contents.stream,pkt.contents.size,pkt.contents.duration
	#print	frame.contents.duration
	ffmpeg.FreePacket(pkt,1)
	



def	test1():
	pass


if	__name__=='__main__':
	test1()
