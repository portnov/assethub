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

