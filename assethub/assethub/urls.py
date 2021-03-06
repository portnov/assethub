"""assethub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
import django.contrib.auth.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout'),
    url(r'^accounts/changepassword/$', django.contrib.auth.views.password_change, name='chane_password'),
    url(r'^accounts/changepassword/done/$', django.contrib.auth.views.password_change_done, name='password_change_done'),
    url(r'^accounts/resetpassword/$', django.contrib.auth.views.password_reset, name='reset_password'),
    url(r'^accounts/resetpassword/done/$', django.contrib.auth.views.password_reset_done, name='password_reset_done'),
    #url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url('', include('social_django.urls', namespace='social')),
    url(r'^', include('assets.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

