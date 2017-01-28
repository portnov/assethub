from os.path import join

from django import template
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.conf import settings
from django.urls import reverse

from assets.models import Comment, Asset

register = template.Library()

@register.simple_tag
def notify(notification):
    if not notification.data:
        return "invalid notification"
    template_name = notification.data.get('template', None)
    if not template_name:
        return unicode(notification.data)
    try:
        template = get_template(join('assets', 'notification', template_name))
        context = dict(notice=notification, user=notification.recipient, instance=notification.action_object, parent=notification.target, author=notification.actor)
        return template.render(context)
    except TemplateDoesNotExist:
        return "template does not exist: " + template_name
    

