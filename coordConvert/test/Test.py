'''
Created on 2012-8-2

@author: Administrator
'''
import urllib
import urllib2
import json

def test():
    url = "http://search1.mapabc.com/sisserver?config=RGC&resType=json&x1=116.8&y1=39.8&x2=116.9&y2=38.87&cr=0&a_k=facd0bc564c82ee2f4603cad5a20c4955b5cb78f3e1c3d88f36e3ddf69c5b44c56ac484ad2e7f508&flag=true"
    data = urllib2.urlopen(url).read()
    data2 = json.loads(data)
    
    print data2["list"]
if __name__=='__main__':
    test();