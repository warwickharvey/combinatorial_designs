from django.conf.urls import patterns, url

from golf import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<num_groups>\d+)x(?P<group_size>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<num_groups>\d+)x(?P<group_size>\d+)/submit_upper_bound$', views.submit_upper_bound, name='submit_upper_bound'),
)

