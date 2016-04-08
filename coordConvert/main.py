#--coding:utf-8--
'''
Created on 2012-8-2

@author: Administrator
'''
import time
from dbconn  import *
import json
import urllib
import urllib2

dbconn = None        
def getDbConn():
    import psycopg2 as pg2
    global dbconn
    
    try:
        if not dbconn:
            dbconn = pg2.connect(host='localhost',#db['host'],
                            database='DVR',#db['name'],
                            port='5432',#db['port'],
                            user='postgres',#db['user'],
                            password='',#db['passwd']
                            )
    except:
        pass
        
    return dbconn

#post方式将真实GPS坐标转换为偏移坐标
def real2skewing_post(coords):
    url = "http://search1.mapabc.com/sisserver"
    values = {'config':'RGC','resType':'json','cr':'0', 'a_k': 'facd0bc564c82ee2f4603cad5a20c4955b5cb78f3e1c3d88f36e3ddf69c5b44c56ac484ad2e7f508','flag':'true'}
    coordict ={}
    coordsStr =""
    for i,coord in enumerate(coords):
#        x = "&x"+ str(i)+"="+str(coord['x'])
#        y = "&y"+ str(i)+"="+str(coord['y'])
        x = str(coord['x'])
        y = str(coord['y'])
        c = x+","+y+";"
        coordsStr += c
    coordict['coors'] = coordsStr
    values.update(coordict)   
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    jsondata = response.read()
    
    data = json.loads(jsondata)
    resCoords = data["list"]
    return resCoords
#    for rescoord in resCoords:
#        print rescoord['x'],rescoord['y']
#        #将数据插入到数据库
        
#get方式将真实GPS坐标转换为偏移坐标,每次转换数量有限制
def real2skewing_get(coords):
    baseStr = "http://search1.mapabc.com/sisserver?config=RGC&resType=json&cr=0&a_k=facd0bc564c82ee2f4603cad5a20c4955b5cb78f3e1c3d88f36e3ddf69c5b44c56ac484ad2e7f508&flag=true"
    coordsStr =""#&coords="
    for i,coord in enumerate(coords):
        x = "&x"+ str(i+1)+"="+str(coord['x'])
        y = "&y"+ str(i+1)+"="+str(coord['y'])
#        x = str(coord['x'])
#        y = str(coord['y'])
        c = x+","+y+";"
        coordsStr += c
    url = baseStr + coordsStr    
    jsondata = urllib2.urlopen(url).read()
    data = json.loads(jsondata)
    resCoords = data["list"]
    return resCoords


#从取出真实坐标,得到地图坐标,更新至数据库的一次循环    
def doConvert():
    print("begin Convert")
    try:
        db = getDbConn()
        cr = db.cursor()
        sql = 'select * from gps_log  where lon_map is null or lat_map is null   ORDER BY "id" limit 10'  #取符合的10条记录
        cr.execute(sql)
        rs = fetchallDict(cr) #取得所有符合条件的所有记录
        #print '-------------------------------------------------------------------'
        #print r
        if rs:
            coords =[]
            for r in rs:
                coord = {}
                coord["id"]= r['id']
                coord["x"] = r['lon']
                coord["y"] = r['lat']
                coords.append(coord)
                
            resCoords = real2skewing_post(coords)  #数组里包含字典
            
            for r,resCoord in zip(rs,resCoords):
                id = r['id']
                lon_map = "%.5f" % float(resCoord['x'])  #保留五位小数
                lat_map = "%.5f" % float(resCoord['y'])  #保留五位小数
                sql = "update gps_log set lon_map=%s,lat_map=%s where id=%s"
                cr.execute(sql,(lon_map,lat_map,id))
            db.commit()
        
    except:
        traceback.print_exc()

def convert_loop():
    while True:
        print 'next Convert'
        doConvert()
        time.sleep(5)


#程序入口
if __name__=='__main__':
    #开始轮询的执行坐标转换
    convert_loop();
