
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def google_plus_client_id():
    return settings.SOCIAL_AUTH_GOOGLE_PLUS_KEY

