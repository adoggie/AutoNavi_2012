# -- coding:utf-8 --

#initdb.py
#初始化系统数据
#----------------------------------------------------------------------------#


import socket,traceback,os,os.path,sys,time,struct,base64,gzip,array,threading

from ConfigParser import ConfigParser
from mutex import mutex as Mutex
import string

from appconfig import SimpleConfig
#----------------------------------------------------------------------------#
aolist=[
		{ 'name':'K.5H773','dasid':'das001','running':0,'iconurl':'null',
			'modules':[
				{'type':1,'hwid':'sn-0001','svcname':'gps_simulator','conurl':'','delta':''}, #gps模拟模块1				
			],
			'client':'tiger'			
		},
]

clients=[
	{'name':'client1','sid':'tiger'},
]

users=[
	{'name':'user1','user':'user1','passwd':'111111',
	 'client':'tiger','sid':'u1'}
]

ao_group=[
	{'name':u'shanghai Traigle Tech.','iconurl':'','client':'tiger','sid':'g1'},
	#{'name':u'上海酷宝信息技术','iconurl':'','user':'user1','sid':'g2'},
	#{'name':u'上海交大汉芯科技','iconurl':'','user':'user1','sid':'g3'},
	#{'name':u'北京神州泰岳技术','iconurl':'','user':'user1','sid':'g4'},
	#{'name':u'上海永生城信技术','iconurl':'','user':'user1','sid':'g5'},
	#{'name':u'上海亚太神通计算机','iconurl':'','user':'user1','sid':'g6'},
	#{'name':u'上海市园林工程公司','iconurl':'','user':'user1','sid':'g7'},
	#{'name':u'英创软件','iconurl':'','user':'user1','sid':'g7'},
	#{'name':u'华东电脑','iconurl':'','user':'user1','sid':'g7'},
	#{'name':u'北京合众思壮','iconurl':'','user':'user1','sid':'g7'},
	#{'name':u'上海联盈数码科技','iconurl':'','user':'user1','sid':'g7'},
	#{'name':u'上海无线通信设备','iconurl':'','user':'user1','sid':'g7'},
]

user_aos={
	'user1':['K.5H773','F.WP655'],
}

aogroup_aos={
	u'shanghai Traigle Tech.':['K.5H773'],
}



#----------------------------------------------------------------------------#
class DataInitializer:
	def __init__(self):				
		self.rpcAdapter = None
		
		self.services=[]
		self.serviceid='' #das id
		self.GM = None
		self.init()
		
	#初始化配置信息 
	def initConfigs(self):
		self.config = SimpleConfig()
		self.config.load('dtuconfig.txt')
		#django 初始化配置 
		os.environ['DJANGO_SETTINGS_MODULE'] = self.config.getValue('django_module')
		sys.path.append(self.config.getValue('django_module_path'))
		
		self.GM = __import__('giscore.models')  #导入数据库模型
		print dir(self.GM.models)
		self.GM = self.GM.models
		
	def init(self):
		try:
			self.initConfigs()
			self.reset_data()
			self.init_data()
		except:
			print traceback.format_exc().decode('utf8')
		
	def reset_data(self):
		self.GM.AO_Module.objects.all().delete()
		self.GM.ActiveObject.objects.all().delete()
		self.GM.AO_AppGroup.objects.all().delete()
		
		#self.GM.NormalUser.objects.all().delete()
		self.GM.AppClient.objects.all().delete()
		
	def init_data(self):
		#初始化客户数据
		for c in clients:
			clt = self.GM.AppClient()
			clt.name = c['name']
			clt.sid = c['sid']
			clt.save()
		for u in users:
			user = self.GM.AppUser()			
			c = self.GM.AppClient.objects.get(sid=u['client'])
			user.client = c
			user.name = u['name']
			user.user = u['user']
			user.passwd = u['passwd']
			user.save()
		for g in ao_group:
			gg = self.GM.AO_AppGroup()
			gg.name = g['name']
			gg.iconurl = g['iconurl']
			c = self.GM.AppClient.objects.get(sid=g['client'])
			gg.client = c
			gg.save()
		for ao in aolist:
			aoh = self.GM.ActiveObject()
			c = self.GM.AppClient.objects.get(sid=ao['client'])
			aoh.client = c
			aoh.name = ao['name']
			aoh.iconurl = ao['iconurl']
			aoh.running = ao['running']
			aoh.dasid = ao['dasid']
			aoh.save()
			#each module saving...
			for m in ao['modules']:
				mh = self.GM.AO_Module()
				mh.ao =aoh
				mh.conurl = m['conurl']
				mh.hwid = m['hwid']
				mh.delta = m['delta']
				mh.svcname = m['svcname']
				mh.type = m['type']
				mh.save()
		# ao and user
		#for k,aos in user_aos.items():
		#	u = self.GM.NormalUser.objects.get(name=k)
		#	for ao in aos:
		#		aoh = self.GM.ActiveObject.objects.get(name=ao)
		#		u.aos.add(aoh)
		# ao and group
		for k,aos in aogroup_aos.items():
			g = self.GM.AO_AppGroup.objects.get(name=k)
			for ao in aos:
				aoh = self.GM.ActiveObject.objects.get(name=ao)
				g.aos.add(aoh)
			g.save()
			
		
if __name__=='__main__':
	server = DataInitializer()
	
					
	