import os,sys,socket,traceback,time,os.path


s = socket.socket()

strdir='ks108.log'

logfile = open(strdir,'a')

line="*0000,A001-0123456789,BP06,250712,092447,121233064,31104502,004,355,00#"
line="*0000,A001-0123456789,BP09,260712,024913,121233109,31104211,000,000,00#"

s.connect(("localhost",15800))
s.sendall(line)
s.close()
