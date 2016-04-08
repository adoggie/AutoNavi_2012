# -- coding:utf-8 --

#影像标签类型定义
class ImageTagTypes:
	ROAD_FLAG = 0x01


class AppUserTypes:
	ROOT 		= 1		#系统管理员
	OPERATOR 	= 1<<1	#生产作业员      # 不能删不能移不能打TAG
	PREVIEWER 	= 1<<2	#影像预处理员    #
	PREVIEW_CHKER = 1<<3	#影像检查员
	DATA_CHKER = 1<<4	#数据检查员
	UNDEF = 1<< 20

class ImageCheckReason:
	ERR_SUCC=0


#系统属性定义
class  SysConstantDefs:
	CAPTURE_SCREEN_KEYS="^space"
	KEYMAPS={
		'ctrl':None
	}



#系统用户
class AppUser:
	def __init__(self):
		self.type = AppUserTypes.UNDEF
		self.name = None
		self.passwd = None
		self.d = None
		self.id = 0

class AppInstance:
	def __init__(self):
		self.user = None
		self.app = None
		#self.wndhotkeys = None #播放窗体热键
		self.tagkeys = None	#标记表 大类小雷 [ {name,key,subclss:[{name,key},..]},
		self.hotkeys=[]									# ..]

	def addHotKey(self,key):
		self.hotkeys.append(key)


	def onUserLogin_Ok(self,user):
		self.user = user
		self.app.login()

	def winEventFilter(self,msg):
		for k in self.hotkeys:
			k.processMsg(msg)

	_handle = None
	@classmethod
	def instance(cls):
		if not cls._handle:
			cls._handle = cls()
		return cls._handle


		
'''
arrows definations: 
right - 前进5秒
left - 后退5秒
up - 快放 x2
down - 慢放 /2 
space - 停止播放/继续播放
alt+space - 暂停，截屏，弹出选择目录窗口


'''

'''
class HotKeyItem:
	def __init__(self):
		pass
'''

