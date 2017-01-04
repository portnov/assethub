from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from taggit.models import Tag

from models import Asset, Component, Application
from forms import AssetForm

PER_PAGE=30

def get_page(request, list):
    paginator = Paginator(list, PER_PAGE)
    page = request.GET.get('page')
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    return result

def index(request):
    if request.user.is_authenticated:
        return user_feed(request, request.user)
    else:
        return full_feed(request)

def full_feed(request):
    asset_list = Asset.objects.order_by('-pub_date')
    assets = get_page(request, asset_list)
    context=dict(assets=assets, title='Last uploads')
    return render(request, 'assets/index.html', context)

def user_feed(request, user):
    asset_list = Asset.objects.filter(author__follower=user.profile).order_by('-pub_date')
    assets = get_page(request, asset_list)
    title = "Feed for user {0}".format(user.get_full_name())
    context=dict(assets=assets, title=title)
    return render(request, 'assets/index.html', context)

def by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    assets = Asset.objects.filter(tags=tag).order_by('-pub_date')
    title = "Assets with tag {}".format(tag.name)
    context = dict(assets = assets, tag=tag.name, title=title)
    return render(request, 'assets/index.html', context)

def by_application(request, appslug):
    app = get_object_or_404(Application, slug=appslug)
    asset_list = Asset.objects.filter(application=app).order_by('-pub_date')
    assets = get_page(request, asset_list)
    title = "Assets for application {}".format(app.title)
    context = dict(assets = assets, application=app, title=title, logo=app.logo)
    return render(request, 'assets/index.html', context)

def by_component(request, appslug, cslug):
    app = get_object_or_404(Application, slug=appslug)
    component = get_object_or_404(Component, application=app, slug=cslug)
    title = "{} assets".format(component)
    asset_list = Asset.objects.filter(application=app, component=component).order_by('-pub_date')
    assets = get_page(request, asset_list)
    context = dict(assets = assets, application=app, component=component, title=title, logo=app.logo)
    return render(request, 'assets/index.html', context)

def by_app_tag(request, appslug, tslug):
    app = get_object_or_404(Application, slug=appslug)
    tag = get_object_or_404(Tag, slug=tslug)
    asset_list = Asset.objects.filter(application=app, tags=tag).order_by('-pub_date')
    assets = get_page(request, asset_list)
    title = "Assets for application {0} with tag {1}".format(app.title, tag.name)
    context = dict(assets = assets, title=title, logo=app.logo)
    return render(request, 'assets/index.html', context)

def by_component_tag(request, appslug, cslug, tslug):
    app = get_object_or_404(Application, slug=appslug)
    component = get_object_or_404(Component, application=app, slug=cslug)
    tag = get_object_or_404(Tag, slug=tslug)
    asset_list = Asset.objects.filter(application=app, component=component, tags=tag).order_by('-pub_date')
    assets = get_page(request, asset_list)
    title = "{0} assets with tag {1}".format(component, tag.name)
    context = dict(assets = assets, title=title, logo=app.logo)
    return render(request, 'assets/index.html', context)

def asset_details(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    context = dict(asset=asset, title=str(asset))
    return render(request, 'assets/asset.html', context)

def vote(request, asset_id, direction):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    if direction not in ["up", "down"]:
        raise Http404("Invalid voting direction")
    asset = get_object_or_404(Asset, pk=asset_id)
    if request.user.is_authenticated:
        if request.user == asset.author:
            return JsonResponse({'succes': False, 'error_message': "Sorry, you can't vote for your own assets"})
        if direction == "up":
            asset.votes.up(request.user.pk)
        else:
            asset.votes.down(request.user.pk)
        response = JsonResponse({'score': asset.votes.count(), 'success': True})
        return response
    else:
        return HttpResponseForbidden()

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

@login_required
def post_asset(request):
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            new_asset = form.save(commit=False)
            new_asset.author = request.user
            new_asset.pub_date = timezone.now()
            new_asset.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('asset', args=[new_asset.pk]))
    else:
        form = AssetForm()

    title = "Post an asset"
    context = dict(post_form=form, title=title, form_action=reverse('post_asset'))
    return render(request, 'assets/post.html', context)

@login_required
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if asset.author != request.user:
        return HttpResponseForbidden("You can edit only your own assets")
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            new_asset = form.save(commit=False)
            new_asset.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('asset', args=[new_asset.pk]))
    else:
        form = AssetForm(instance=asset)

    title = "Edit an asset"
    context = dict(post_form=form, title=title, form_action=reverse('edit_asset', args=[pk]))
    return render(request, 'assets/post.html', context)

