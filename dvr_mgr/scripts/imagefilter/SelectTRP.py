#!/usr/bin/env python
#coding=utf-8

import os
import string
import ConfigParser


class SelectTRP():
	def __init__(self):
		self.read_config()
		self.XYpoint1 = self.XYpoint1.split(',')
		self.XYpoint2 = self.XYpoint2.split(',')
		
		self.X_point1 = float(self.XYpoint1[0])*self.XYframe
		self.Y_point1 = float(self.XYpoint1[1])*self.XYframe
		self.X_point2 = float(self.XYpoint2[0])*self.XYframe
		self.Y_point2 = float(self.XYpoint2[1])*self.XYframe
		
		self.trpfile_list = []
	
	def read_config(self):
		read_trpconfig = ConfigParser.ConfigParser()
		try:
			sele_trpconfig = open(os.path.join(os.getcwd(),'sele_trpconfig.ini'))
		except WindowsError:
			print '%s not found,please check out !' %('sele_trpconfig.ini')
			main_pause = raw_input('press enter for exit'.encode('gbk'))
			sys.exit(1)
		read_trpconfig.readfp(sele_trpconfig)
		
		self.XYframe = int(read_trpconfig.get('sele_trpconfig','XYframe'))
		self.trp_path = read_trpconfig.get('sele_trpconfig','TRP_Path').decode('gbk')
		self.XYpoint1 = read_trpconfig.get('sele_trpconfig','XYPoint1')
		self.XYpoint2 = read_trpconfig.get('sele_trpconfig','XYPoint2')
		self.judge_within = int(read_trpconfig.get('sele_trpconfig','judge_within'))
		self.result_file = read_trpconfig.get('sele_trpconfig','result_file').decode('gbk')

	def within(self,trpfile):
		avail_count = 0
		open_trpfile = open(trpfile,'r')
		trp_data = map(string.strip,open_trpfile.readlines())
		for trp_line in trp_data:
			xy_list = trp_line.split(',')
			if len(xy_list) > 1:
				X_trp = float(xy_list[0])
				Y_trp = float(xy_list[1])
				if X_trp >= self.X_point1 and X_trp <= self.X_point2 and Y_trp >= self.Y_point1 and Y_trp <= self.Y_point2:
					avail_count += 1
				if avail_count > self.judge_within:
					return 1
		return 0

if __name__ == '__main__':
	print "Search trp file,pelease watting ... "
	trp_inst = SelectTRP()
	try:
		write_result = open(trp_inst.result_file,'w')
	except WindowsError:
			print '\n\n%s not found,please check out !' %(trp_inst.result_file)
			main_pause = raw_input('press enter for exit'.encode('gbk'))
			sys.exit(1)

	for root,dirs,files in os.walk(trp_inst.trp_path):
		for filename in files:
			if filename[-3:] == 'trp':
				# filename = filename.decode('gbk')
				trp_inst.trpfile_list.append(os.path.join(root,filename))

	count = 0
	filecount = len(trp_inst.trpfile_list)

	print "\n\n%s trp files,calculating the data ..." %(filecount)
	for trpfile in trp_inst.trpfile_list:
		if trp_inst.within(trpfile) == 1:
			count += 1
			print "%s/%s,filename:%s".decode('utf-8') %(count,filecount,os.path.basename(trpfile))
			trpfile = trpfile.encode('gbk')
			trpmedia = r"%s\100MEDIA\%s.mov" %(os.path.dirname(os.path.dirname(trpfile)),os.path.splitext(os.path.basename(trpfile))[0])
			write_result.write("%s\n" %(trpfile))
			write_result.write("%s\n" %(trpmedia))
			write_result.flush()

	write_result.close()
	main_pause = raw_input('\n\nsuccessfully,press enter for exit'.encode('gbk'))











