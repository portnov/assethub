
from django import template

from taggit.models import Tag

from assets.models import Application

register = template.Library()

@register.inclusion_tag('assets/tree.html')
def tree():
    apps = Application.objects.all()
    return {'applications': apps}

@register.inclusion_tag('assets/tags.html')
def tags():
    tags = Tag.objects.all()
    return {'tags': tags}

@register.inclusion_tag('assets/pagination.html')
def pagination(objects):
    return {'objects': objects}

