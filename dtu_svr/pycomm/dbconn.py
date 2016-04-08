# -*- coding:gb2312 -*-
import sys, traceback,threading,time

PY26=False
if sys.version_info[1]==6: #  python 2.6 use psycopg2
	import psycopg2
	PY26 = True
else:
	sys.path.append('pgsql')
	import pgsql

'''
http://www.python.org/dev/peps/pep-0249/
'''

####END CLASS ######################################


def __fetchoneDict2(cursor):
	row ={}
	rs = cursor.fetchone()
	flds = cursor.description
	if rs == None:
		return None
	
	for i in range(len(flds)):
		row[flds[i][0]] = rs[i]	
	return row

def __fetchallDict2(cursor):
	dict =[]
	rs = cursor.fetchall()
	if len(rs) ==0:
		return dict
	flds = cursor.description
	for r in rs:
		row = {}
		for i in range(len(flds)):
			row[flds[i][0]] = r[i]
		dict.append(row)
	return dict


def fetchoneDict(cursor):
	if PY26:
		return __fetchoneDict2(cursor)
	
	row ={}
	rs = cursor.fetchone()
	flds = cursor.fields
	if rs == None:
		return None
	
	for i in range(len(flds)):
		row[flds[i]] = rs[i]
	
	return row

def fetchallDict(cursor):
	if PY26:
		return __fetchallDict2(cursor)
	dict =[]
	rs = cursor.fetchall()
	if len(rs) ==0:
		return dict
	flds = cursor.fields
	for r in rs:
		row = {}
		for i in range(len(flds)):
			row[flds[i]] = r[i]
		dict.append(row)
	return dict				

def prepareRecordset(cr,maxRows=-1):
	'''
	to see sts.ice
	'''	
	rows =[]
	rset = stsRecordSet()
	if maxRows == -1:
		rows = cr.fetchall()
	else:
		rows = cr.fetchmany(maxRows)
	for row in rows:
		rr = map(str,row)		
		rset.rows.append(rr)				
	for f in cr.fields:
		rset.fields.append(f)				#装配字段数组
	return rset

