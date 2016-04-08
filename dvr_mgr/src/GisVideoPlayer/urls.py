from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^kqstock/', include('kqstock.foo.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

	(r'^$', 'stockmain.member_login_page'),
	(r'^do_member_login$', 'stockmain.do_member_login'),
	
	(r'^admin/$', 'stockmain.admin_login_page'),
	(r'^do_admin_login$', 'stockmain.do_admin_login'),
	(r'^getAfmServer/$', 'stockmain.getAfmServer'),
	(r'^gateway/$', 'amfgateway.gateway'),
	(r'^gateway$', 'amfgateway.gateway'),
	(r'^medias/(?P<path>.*)$', 'django.views.static.serve',{'document_root': './medias'}),
	(r'^importClients/$', 'server.importClients'),
	(r'^importGoods/$', 'server.importGoods'),
)