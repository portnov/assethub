from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.by_tag, name='by_tag'),
    url(r'^asset/(?P<pk>[0-9]+)/$', views.asset_details, name='asset'),
    url(r'^asset/(?P<pk>[0-9]+)/edit/$', views.edit_asset, name='edit_asset'),
    url(r'^vote/(?P<asset_id>[0-9]+)/(?P<direction>up|down)/$', views.vote, name='vote'),
    url(r'^accounts/profile/(?P<username>[-\w]+)$', views.user_profile, name='user_profile'),
    url(r'^accounts/profile/$', views.current_user_profile, name='current_user_profile'),
    url(r'^post/$', views.post_asset, name='post_asset'),
    url(r'^(?P<appslug>[-\w]+)/$', views.by_application, name='by_application'),
    url(r'^(?P<appslug>[-\w]+)/tag/(?P<tslug>[-\w]+)/$', views.by_app_tag, name='by_app_tag'),
    url(r'^(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/$', views.by_component, name='by_component'),
    url(r'^(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/tag/(?P<tslug>[-\w]+)/$', views.by_component_tag, name='by_component_tag')
]
