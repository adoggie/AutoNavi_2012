#-*- coding=utf-8 -*
'''
Created on 2012-4-5

@author: DTR
'''
from django.conf.urls.defaults import patterns,url
from strategy.views import *
from system.views import requires_login

urlpatterns = patterns('strategy.views',
    
    url(r'^area/group/add/$',requires_login(area_group_add),name='area_group_add'),
    url(r'^area/add/$',requires_login(area_add),name='area_add'),
    url(r'^area/edit/(?P<area_id>\d+)/$',requires_login(area_edit),name="area_edit"),
    url(r'^area/list/$',requires_login(area_list),name="area_list"),
    url(r'^area/views/$',requires_login(area_view),name="area_view"),
    url(r'^area/delete/(?P<area_id>\d+)/$', requires_login(area_delete),name="area_delete"),
    
    url(r'^strategy_add/$',requires_login(strategy_add),name='strategy_add'),
    url(r'^strategy/group/add/$',requires_login(strategy_group_add),name='strategy_group_add'),
    url(r'^strategy/edit/(?P<strategy_id>\d+)/$',requires_login(strategy_edit),name="strategy_edit"),
    url(r'^strategy/list/$', requires_login(strategy_list),name="strategy_list"),
    url(r'^strategy/delete/$', requires_login(strategy_delete),name="strategy_delete"),
    url(r'^area/getarea/(?P<areagroup_id>\d+)/$', requires_login(get_area_by_group),name="strategy_delete"),
    
    url(r'^vehicle/strategy/$',requires_login(vehicle_strategy),name="vehicle_strategy"),
    url(r'^vehicle/getstrategy/(?P<vehicle_id>\d+)/$',requires_login(vehicle_getstrategy),name="vehicle_strategy"),
    url(r'^assign_stragety/$',requires_login(assign_stragety),name="assign_stragety"),
#    url(r'^lib_edit/(?P<lib_id>\d*)/$', requires_login(lib_edit)),
#    url(r'^lib_edit/$', requires_login(lib_edit)),
    
)
