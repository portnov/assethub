from django.conf.urls import url, include

#from rest_framework import routers

import views.asset
import views.users
import rest
#import serializers

#router = routers.DefaultRouter()
#router.register(r'assets', serializers.AssetViewSet)

urlpatterns = [
    url(r'^$', views.asset.index, name='index'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
#    url(r'^api/', include(router.urls)),
    url(r'^api/search/$', rest.SearchList.as_view()),
    url(r'^api/applications/(?P<appslug>[-\w]+)/$', rest.ComponentList.as_view()),
    url(r'^api/applications/$', rest.ApplicationList.as_view()),
    url(r'^api/licenses/$', rest.LicenseList.as_view()),
    url(r'^api/assets/$', rest.AssetList.as_view()),
    url(r'^api/assets/(?P<pk>\d+)/$', rest.AssetDetail.as_view()),
    url(r'^api/assets/(?P<appslug>[-\w]+)/$', rest.AssetList.as_view()),
    url(r'^api/assets/(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/$', rest.AssetList.as_view()),
    url(r'^search/$', views.asset.simple_search, name='simple_search'),
    url(r'^search/advanced/$', views.asset.advanced_search, name='advanced_search'),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.asset.by_tag, name='by_tag'),
    url(r'^asset/(?P<pk>[0-9]+)/$', views.asset.asset_details, name='asset'),
    url(r'^asset/(?P<pk>[0-9]+)/edit/$', views.asset.edit_asset, name='edit_asset'),
    url(r'^vote/(?P<asset_id>[0-9]+)/(?P<direction>up|down)/$', views.asset.vote, name='vote'),
    url(r'^license/(?P<slug>[-\w]+)/$', views.asset.license, name='license'),
    url(r'^accounts/profile/(?P<username>[-\w]+)/follow/$', views.users.follow, name='follow_user'),
    url(r'^accounts/profile/(?P<username>[-\w]+)/unfollow/$', views.users.unfollow, name='unfollow_user'),
    url(r'^accounts/profile/(?P<username>[-\w]+)/feed/$', views.asset.get_user_feed, name='user_feed'),
    url(r'^accounts/profile/edit/$', views.users.edit_profile, name='edit_profile'),
    url(r'^accounts/profile/(?P<username>[-\w]+)$', views.users.user_profile, name='user_profile'),
    url(r'^accounts/profile/$', views.users.current_user_profile, name='current_user_profile'),
    url(r'^accounts/$', views.users.get_users_list, name='users_list'),
    url(r'^post/(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/$', views.asset.post_asset, name='post_asset'),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^(?P<appslug>[-\w]+)/$', views.asset.by_application, name='by_application'),
    url(r'^(?P<appslug>[-\w]+)/version/(?P<verstring>[0-9.]+)/$', views.asset.by_version, name='by_version'),
    url(r'^(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/version/(?P<verstring>[0-9.]+)/$', views.asset.by_component_version, name='by_component_version'),
    url(r'^(?P<appslug>[-\w]+)/tag/(?P<tslug>[-\w]+)/$', views.asset.by_app_tag, name='by_app_tag'),
    url(r'^(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/$', views.asset.by_component, name='by_component'),
    url(r'^(?P<appslug>[-\w]+)/(?P<cslug>[-\w]+)/tag/(?P<tslug>[-\w]+)/$', views.asset.by_component_tag, name='by_component_tag')
]

