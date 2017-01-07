from django import template
from django.contrib.flatpages.models import FlatPage

from flatmenu.models import MenuItem

register = template.Library()

class MenuNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name

    def render(self, context):
        menu_items = MenuItem.objects.order_by('seq')
        context[self.context_name] = menu_items
        return ''

@register.tag
def get_menu_items(parser, token):
    bits = token.split_contents()

    error_message = "%(tagname)s expects a syntax of: %(tagname)s as context_name".format(dict(tagname=bits[0]))
    if len(bits) != 3:
        raise template.TemplateSyntaxError(error_message)
    if bits[1] != "as":
        raise template.TemplateSyntaxError(error_message)

    context_name = bits[-1]
    return MenuNode(context_name)

