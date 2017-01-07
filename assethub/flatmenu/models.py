from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

class MenuItem(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(max_length=32)
    seq = models.PositiveIntegerField(default=0, unique=True, verbose_name=_("Order"))
    flatpage = models.ForeignKey(FlatPage, verbose_name=_("Page"), on_delete=models.CASCADE, null=True, blank=True)
    url = models.URLField(_("URL"), null=True, blank=True)

    def clean(self):
        super(MenuItem, self).clean()
        if self.flatpage and self.url:
            raise ValidationError(_("Page and URL can not be specified simultaneously"))
        if not self.flatpage and not self.url:
            raise ValidationError(_("You should specify either page or URL"))

    def get_url(self):
        if self.url:
            return self.url
        elif self.flatpage:
            return reverse('django.contrib.flatpages.views.flatpage', kwargs={'url': self.flatpage.url})
        else:
            return None

    def __str__(self):
        return self.title.encode('utf-8')

