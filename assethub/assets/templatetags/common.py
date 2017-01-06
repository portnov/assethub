from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html

from django_gravatar.helpers import get_gravatar_url

register = template.Library()

@register.simple_tag
def user_link(user):
    gravatar_url = get_gravatar_url(user.email, size=16)
    profile_url = reverse('user_profile', args=[user.username])
    return format_html("""<a href="{0}"><img class="gravatar-small" src="{1}"/>{2}</a>""", profile_url, gravatar_url, user.get_full_name())

@register.inclusion_tag('assets/asset_title.html')
def asset_title(asset, as_link):
    return {'asset': asset, 'as_link': as_link}

@register.inclusion_tag('assets/asset_common.html')
def asset_common(asset, verbose):
    return {'asset': asset, 'verbose': verbose}

