import os,sys,socket,traceback,time,os.path


s = socket.socket()
s.bind(('',15800))
s.listen(5)

strdir='ks108.log'

logfile = open(strdir,'a')

dtu = None
while True:
	print 'waiting ks108 new connection...'
	try:
		dtu,a = s.accept()
		print a
		while True:
			d = dtu.recv(1000)
			if not d:
				break
			print d
			dtu.sendall('*0000,000013916624477,AP06,01,121.345,31.12,0.04,0.04,2012,06,12,12,16#')
			tt = time.localtime()
			#print tt
			logfile.write(d)
			logfile.write('\n')
			logfile.flush()
			print time.asctime()		
	except:		
		if dtu:
			dtu.close()
		traceback.print_exc()
	