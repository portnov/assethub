from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from taggit.models import Tag
from versionfield.utils import convert_version_string_to_int

from assets.models import Asset, Component, Application, License

# TODO; this should be configurable
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

def get_assets_query(appslug=None, app=None,
            cslug=None, component=None,
            tslug=None, tags=None,
            follower=None,
            verstring=None, version=None,
            asset_version=None,
            license=None,
            asset_title=None,
            author=None,
            original_author=None,
            order_by='-pub_date', **kwargs):

    qry = Q()
    auto_title = []
    if appslug is not None:
        app = get_object_or_404(Application, slug=appslug)
    if app is not None:
        auto_title.append(_("application {}").format(app.title))
        qry = qry & Q(application=app)
    if cslug is not None and app is not None:
        component = get_object_or_404(Component, application=app, slug=cslug)
    if component is not None:
        auto_title.append(_("component {}").format(component.title))
        qry = qry & Q(component=component)
    if tslug is not None:
        tag = get_object_or_404(Tag, slug=tslug)
        auto_title.append(_("tag {}").format(tag.name))
        qry = qry & Q(tags=tag)
    if tags is not None:
        tags_title = ", ".join([tag.name for tag in tags])
        auto_title.append(_("tags {}").format(tags_title))
        qry = qry & Q(tags__in=tags)
    if asset_title:
        auto_title.append(_("title contains `{}'").format(asset_title))
        qry = qry & Q(title__contains=asset_title)
    if author is not None:
        auto_title.append(_("author is {}").format(author.get_full_name()))
        qry = qry & Q(author=author)
    if original_author:
        auto_title.append(_("original author {}").format(original_author))
        qry = qry & Q(original_author__contains=original_author)
    if license is not None:
        auto_title.append(_("license {}").format(license))
        qry = qry & Q(license=license)
    if follower is not None:
        qry = qry & Q(author__follower=follower.profile)
        auto_title.append(_("from users followed by {}").format(follower.get_full_name()))
    if verstring is not None and app is not None:
        try:
            version = convert_version_string_to_int(verstring, [8,8,8,8])
        except (ValueError, NotImplementedError):
            raise Http404
    if version is not None and app is not None:
        if not verstring:
            verstring = str(version)
        auto_title.append(_("compatible with application version {}").format(version))
        qry = qry & (Q(application=app) & (Q(app_version_min__lte=verstring) | Q(app_version_min=None)) & (Q(app_version_max__gte=verstring) | Q(app_version_max=None)))
    if asset_version is not None:
        auto_title.append(_("version is {}").format(asset_version))
        qry = qry & Q(version=asset_version)

    return qry, auto_title

def get_simple_search_qry(query):
    qry = Q(title__contains=query)
    qry = qry | Q(application__slug=query)
    qry = qry | Q(component__slug=query)
    qry = qry | Q(author__username__contains=query)
    qry = qry | Q(original_author__contains=query)
    try:
        tag = Tag.objects.get(slug=query)
    except Tag.DoesNotExist:
        tag = None
    else:
        qry = qry | Q(tags=tag)
    return qry

