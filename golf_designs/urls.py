from django.conf.urls import patterns, url

from golf_designs import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<num_groups>\d+)x(?P<group_size>\d+)/$', views.detail, name='detail'),
)

