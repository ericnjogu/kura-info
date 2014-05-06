from django.conf.urls.defaults import patterns, handler404, handler500

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('kura_web.views',
    (r'^$', 'index'),
    (r'^about/$', 'about'),
    (r'^constituencies/page/(?P<page_num>[12]{1})/$', 'constics'),
    (r'^constituencies/alphabetical/(?P<letter>[a-zA-Z]{1})/page/(?P<page_num>\d+)/$', 'constics_starting_with'), 
    (r'^constituencies/(?P<const_name>[a-zA-Z ]+)/page/(?P<page_num>\d+)/$', 'poll_stations_for'),
    #TODO refine the stn_name regex to allow names like KAREN "C"
    #(r'^constituencies/(?P<const_name>[a-zA-Z ]+)/(?P<stn_name>[0-9a-zA-Z" ]+)/$', 'view_pollstation'),
    (r'^constituencies/(?P<const_name>[a-zA-Z ]+)/(?P<stn_name>[0-9a-zA-Z". ]+)/$', 'view_pollstation'),
    (r'^constituencies/(?P<const_name>[a-zA-Z ]+)/(?P<stn_name>[0-9a-zA-Z". ]+)/add-directions/$', 'add_pollstation_direction'),
    #(r'^favicon.ico',)

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
