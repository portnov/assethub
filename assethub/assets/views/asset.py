from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from taggit.models import Tag
from versionfield.utils import convert_version_string_to_int

from assets.models import Asset, Component, Application, License
from assets.forms import AssetForm
from assets.views.common import get_page

def show_assets_list(request, assets_list, **kwargs):
    assets = get_page(request, assets_list)
    context=dict(assets=assets, **kwargs)
    return render(request, 'assets/index.html', context)

def show_assets_list_by(request, appslug=None, cslug=None, tslug=None, follower=None, verstring=None, order_by='-pub_date', **kwargs):
    qry = Q()
    app = None
    component = None
    auto_title = []
    if appslug is not None:
        app = get_object_or_404(Application, slug=appslug)
        auto_title.append(_("application {}").format(app.title))
        qry = qry & Q(application=app)
    if cslug is not None and app is not None:
        component = get_object_or_404(Component, application=app, slug=cslug)
        auto_title.append(_("component {}").format(component.title))
        qry = qry & Q(component=component)
    if tslug is not None:
        tag = get_object_or_404(Tag, slug=tslug)
        auto_title.append(_("tag {}").format(tag.name))
        qry = qry & Q(tags=tag)
    if follower is not None:
        qry = qry & Q(author__follower=follower.profile)
        auto_title.append(_("from users followed by {}").format(follower.get_full_name))
    if verstring is not None and app is not None:
        try:
            version = convert_version_string_to_int(verstring, [8,8,8,8])
        except (ValueError, NotImplementedError):
            raise Http404
        auto_title.append(_("compatible with application version {}").format(verstring))
        qry = qry & (Q(application=app) & (Q(app_version_min__lte=verstring) | Q(app_version_min=None)) & (Q(app_version_max__gte=verstring) | Q(app_version_max=None)))

    asset_list = Asset.objects.filter(qry).order_by(order_by)

    title = kwargs.get('title', None)
    if title is None:
        title = _("Assets by criteria") + ": " + ", ".join(auto_title)
        kwargs['title'] = title
    if app is not None:
        kwargs['application'] = app
        kwargs['logo'] = app.logo
    if component is not None:
        kwargs['component'] = component
    return show_assets_list(request, asset_list, **kwargs)

def index(request):
    if request.user.is_authenticated:
        return user_feed(request, request.user)
    else:
        return full_feed(request)

def full_feed(request):
    return show_assets_list_by(request, title=_('Last uploads'))

def get_user_feed(request, username):
    user = get_object_or_404(User, username=username)
    return user_feed(request, user)

def user_feed(request, user):
    title = _("Feed for user {0}").format(user.get_full_name())
    return show_assets_list_by(request, follower=user, title=title)

def by_tag(request, slug):
    return show_assets_list_by(request, tslug=slug)

def by_application(request, appslug):
    return show_assets_list_by(request, appslug=appslug)

def by_component(request, appslug, cslug):
    return show_assets_list_by(request, appslug=appslug, cslug=cslug)

def by_app_tag(request, appslug, tslug):
    return show_assets_list_by(request, appslug=appslug, tslug=tslug)

def by_component_tag(request, appslug, cslug, tslug):
    return show_assets_list_by(request, appslug=appslug, tslug=tslug)

def by_version(request, appslug, verstring):
    return show_assets_list_by(request, appslug=appslug, verstring=verstring)

def by_component_version(request, appslug, cslug, verstring):
    return show_assets_list_by(request, appslug=appslug, cslug=cslug, verstring=verstring)

def asset_details(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    context = dict(asset=asset, title=unicode(asset), application=asset.application, component=asset.component)
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
def post_asset(request, appslug, cslug):
    application = get_object_or_404(Application, slug=appslug)
    component = get_object_or_404(Component, slug=cslug)
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            new_asset = form.save(commit=False)
            new_asset.author = request.user
            new_asset.pub_date = timezone.now()
            new_asset.application = application
            new_asset.component = component
            new_asset.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('asset', args=[new_asset.pk]))
    else:
        form = AssetForm()
        form.application = application
        form.component = component

    title = _("Post an asset")
    context = dict(post_form=form, title=title, application=application, component=component, form_action=reverse('post_asset', args=[appslug, cslug]))
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

    title = _("Edit an asset")
    context = dict(post_form=form, title=title, form_action=reverse('edit_asset', args=[pk]))
    return render(request, 'assets/post.html', context)

def license(request, slug):
    license = get_object_or_404(License, slug=slug)
    context = dict(license=license, title=str(license))
    return render(request, 'assets/license.html', context)

