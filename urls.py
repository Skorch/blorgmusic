from django.conf.urls.defaults import *
from BlorgMusicHandler.ajaxhandler import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^updatesongdata/$', 'BlorgMusicIngestPipeline.updatesongdata.main'),
    (r'^admindata/$', 'BlorgMusicIngestPipeline.admindata.main'),
    (r'^parsetwitter/$', 'BlorgMusicIngestPipeline.twitterhandler.main'),
    (r'^fetchdata/$', 'BlorgMusicIngestPipeline.fetchdata.main'),
    (r'^test/songtitle/$', 'BlorgMusicIngestPipeline.test_songtitleparse.main'),

    (r'^rpc/$', 'BlorgMusicHandler.fetchdata.main'),

    (r'^ws/', include(ws.urls)),

    (r'^$', 'blorgmusic1.views.render'),

)
