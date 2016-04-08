# -- coding:utf-8 --
from django.conf.urls.defaults import patterns, include, url
from system.views import login,logout,index,requires_login,left,top,main
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DVR.views.home', name='home'),
    # url(r'^DVR/', include('DVR.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^login/', login),
     url(r'^logout/', logout),
     url(r'^left/', left),
     url(r'^top/', top),
     url(r'^main/', main),
     url(r'^admin/', include(admin.site.urls)),
     url(r'^index/|^$', requires_login(index)),
     
)
urlpatterns += patterns('',
#    url(r'^confirm/delete/$', uploaTestview.confirm_delete, name='confirm_delete'),
    url(r'^device/', include('device.urls')),
)
urlpatterns += patterns('',
#    url(r'^confirm/delete/$', uploaTestview.confirm_delete, name='confirm_delete'),
    url(r'^system/', include('system.urls')),
)
urlpatterns += patterns('',
#    url(r'^confirm/delete/$', uploaTestview.confirm_delete, name='confirm_delete'),
    url(r'^strategy/', include('strategy.urls')),
)
urlpatterns += patterns('',
#    url(r'^confirm/delete/$', uploaTestview.confirm_delete, name='confirm_delete'),
    url(r'^monitoring/', include('monitoring.urls')),
)