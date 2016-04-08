#-*- coding=utf-8 -*
'''
Created on 2012-4-5

@author: DTR
'''
from django.conf.urls.defaults import patterns,url
from monitoring.views import *
from system.views import requires_login

urlpatterns = patterns('monitoring.views',
    url(r'^track/$', requires_login(track),name="track"),
    url(r'^getTrack/$', requires_login(getTrack),name="getTrack"),
    url(r'^recentTrack/$', requires_login(recentTrack),name="recentTrack"),
    url(r'^getRecentTrack/$',requires_login(getRecentTrack),name="getRecentTrack"),
    url(r'^disposition/$', requires_login(disposition),name="disposition"),
    url(r'^getDisposition/$', requires_login(getDisposition),name="getDisposition"),
    
#    url(r'^lib_edit/(?P<lib_id>\d*)/$', requires_login(lib_edit)),
#    url(r'^lib_edit/$', requires_login(lib_edit)),
    
)
