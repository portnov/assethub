from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from taggit.models import Tag

from assets.models import Asset, Component, Application
from assets.forms import AssetForm, UserForm, ProfileForm
from assets.views.common import get_page

@login_required
def follow(request, username):
    """POST handler for 'follow' AJAX link"""

    if request.method != 'POST':
        return HttpResponseBadRequest()
    buddy = get_object_or_404(User, username=username)
    request.user.profile.follows.add(buddy)
    response = JsonResponse({'success': True})
    return response

@login_required
def unfollow(request, username):
    """POST handler for 'unfollow' AJAX link"""

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
    title = _("{0}'s profile").format(user.username)
    most_rated_assets = user.asset_set.order_by('-num_votes')[:5]
    try:
        followed = request.user.profile.does_follow(user)
    except AttributeError as e:
        print(e)
        followed = False
    context = dict(buddy=user, followed=followed, title=title, most_rated_assets=most_rated_assets)
    return render(request, "assets/profile.html", context)

def get_users_list(request):
    users_list = User.objects.order_by('username')
    users = get_page(request, users_list)
    context = dict(users=users, title = _("List of users"))
    return render(request, "assets/users.html", context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('user_profile', args=[user.username]))
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)

    title = _("Edit profile")
    context = dict(user_form=user_form, profile_form=profile_form, title=title, form_action=reverse('edit_profile'))
    return render(request, 'assets/edit_profile.html', context)

