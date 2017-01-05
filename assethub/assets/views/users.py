from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from taggit.models import Tag

from assets.models import Asset, Component, Application
from assets.forms import AssetForm
from assets.views.common import get_page

@login_required
def follow(request, username):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    buddy = get_object_or_404(User, username=username)
    request.user.profile.follows.add(buddy)
    response = JsonResponse({'success': True})
    return response

@login_required
def unfollow(request, username):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    buddy = get_object_or_404(User, username=username)
    request.user.profile.follows.remove(buddy)
    response = JsonResponse({'success': True})
    return response

def current_user_profile(request):
    if request.user.is_authenticated:
        return get_user_profile(request, request.user)
    else:
        return HttpResponseForbidden()

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return get_user_profile(request, user)

def get_user_profile(request, user):
    title = "{0}'s profile".format(user.username)
    most_rated_assets = user.asset_set.order_by('-num_votes')[:5]
    followed = request.user.profile.does_follow(user)
    context = dict(buddy=user, followed=followed, title=title, most_rated_assets=most_rated_assets)
    return render(request, "assets/profile.html", context)

def get_users_list(request):
    users_list = User.objects.order_by('username')
    users = get_page(request, users_list)
    context = dict(users=users, title = "List of users")
    return render(request, "assets/users.html", context)

