#-*- coding=utf-8 -*
'''
Created on 2012-4-5

@author: DTR
'''
from django.conf.urls.defaults import patterns,url
from system.views import *
from system.views import requires_login

urlpatterns = patterns('device.views',
    url(r'^user_add/$', requires_login(user_add),name='user_add'),
    url(r'^user_delete/(?P<user_id>\d*)/$', requires_login(user_delete),name='user_delete'),
    url(r'^user_edit/(?P<user_id>\d*)/$', requires_login(user_edit),name='user_delete'),
    url(r'^user_list/$', requires_login(user_list),name='user_list'),
    url(r'^changePassword/$', requires_login(changePassword),name='changePassword'),
    
#    url(r'^lib_edit/(?P<lib_id>\d*)/$', requires_login(lib_edit)),
#    url(r'^lib_edit/$', requires_login(lib_edit)),
    
)
