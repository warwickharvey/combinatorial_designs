from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^golf/', include('golf.urls', namespace='golf')),
    url(r'^admin/', include(admin.site.urls)),
)
