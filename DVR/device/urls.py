#-*- coding=utf-8 -*
'''
Created on 2012-4-5

@author: DTR
'''
from django.conf.urls.defaults import patterns,url
from device.views import *
from system.views import requires_login

urlpatterns = patterns('device.views',
    url(r'^$', requires_login(device)),
    url(r'^vehicle/add/$', requires_login(vehicle_add),name="vehicle_add"),
    url(r'^vehicle/edit/(?P<vehicle_id>\d+)/$', requires_login(vehicle_edit),name="vehicle_edit"),
    url(r'^vehicle/list/$', requires_login(vehicle_list),name="vehicle_list"),
#    url(r'^vehicle/delete/(?P<vehicle_id>\d+)/$', requires_login(vehicle_delete),name="vehicle_delete"),
    url(r'^vehicle/delete/$', requires_login(vehicle_delete),name="vehicle_delete"),
    url(r'^group_vehicle/$', requires_login(group_vehicle),name="group_vehicle"),
    url(r'^vehicle/group/add/$', requires_login(vehicle_group_add),name="vehicle_group_add"),
    url(r'^vehicle/group/list/$', requires_login(vehicle_group_list),name="vehicle_group_list"),
    url(r'^vehicle/group/del/$', requires_login(vehicle_group_del),name="vehicle_group_del"),
    url(r'^myvehiclegroup/$', requires_login(myvehiclegroup),name="myvehiclegroup"),
    url(r'^vehicles/(?P<group_id>\d*)/$',requires_login(vehicles_by_group),name="vehicles_by_group"),
#    url(r'^vehicle/vehicle_dtu/(?P<vehicle_id>\d+)/$', requires_login(vehicle_dtu),name="vehicle_edit"),
    url(r'^vehicle/installdate/(?P<vehicle_id>\d*)/$', requires_login(updateInstalldate),name="updateInstalldate"),
    
    url(r'^dtu/add/$', requires_login(dtu_add),name="dtu_add"),
    url(r'^dtu/edit/(?P<dtu_id>\d+)/$', requires_login(dtu_edit),name="dtu_edit"),
    url(r'^dtu/list/$', requires_login(dtu_list),name="dtu_list"),
    url(r'^dtu/delete/$', requires_login(dtu_delete),name="dtu_delete"),
    url(r'^dtu/group/add/$', requires_login(dtu_group_add),name="dtu_group_add"),
    url(r'^dtu/group/del/$', requires_login(dtu_group_del),name="dtu_group_del"),
    url(r'^dtu/group/list/$', requires_login(dtu_group_list),name="dtu_group_list"),
    url(r'^dtus/(?P<group_id>\d*)/$',requires_login(dtus_by_group),name="dtus_by_group"),
    url(r'^group_dtu/$', requires_login(group_dtu),name="group_dtu"),
    url(r'^mydtugroup/$', requires_login(mydtugroup),name="mydtugroup"),
    
    
    url(r'^change_vehicles_group_r/$',requires_login(change_vehicles_group_r),name="change_vehicles_group_r"),
    url(r'^change_dtus_group_r/$',requires_login(change_dtus_group_r),name="change_dtus_group_r"),
    
#    url(r'^lib_edit/(?P<lib_id>\d*)/$', requires_login(lib_edit)),
#    url(r'^lib_edit/$', requires_login(lib_edit)),
    
)
