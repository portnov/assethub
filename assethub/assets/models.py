from __future__ import unicode_literals

from os.path import basename
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django_comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from taggit_autosuggest.managers import TaggableManager
from vote.managers import VotableManager
from versionfield import VersionField

class Application(models.Model):
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title.encode('utf-8')

class Component(models.Model):
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    upload_instructions = models.TextField(null=True, blank=True)
    install_instructions = models.TextField(null=True, blank=True)

    def __str__(self):
        return pgettext_lazy("component title", "{0} {1}").format(self.application.title, self.title).encode('utf-8')

class License(models.Model):
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return pgettext_lazy("license title", "{0}: {1}").format(self.slug, self.title)

class Asset(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("author"))
    application = models.ForeignKey('Application', on_delete=models.CASCADE, verbose_name=_("application"))
    component = models.ForeignKey('Component', on_delete=models.CASCADE, null=True, verbose_name=_("component"))
    license = models.ForeignKey('License', on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("license"))
    original_author = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("original author"))
    creation_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Originally created"))
    title = models.CharField(max_length=255, verbose_name=_("title"))
    notes = models.TextField(null=True, verbose_name=_("description"))
    image = models.ImageField(upload_to='thumbnails/', verbose_name=_("thumbnail"))
    data = models.FileField(upload_to='data/', verbose_name=_("data file"))
    url = models.URLField(null=True, blank=True, verbose_name=_("URL"))
    pub_date = models.DateTimeField(verbose_name=_("date published"))
    version = VersionField(null=True, blank=True, number_bits=[8,8,8,8], verbose_name=_("asset version"))
    app_version_min = VersionField(verbose_name=_("Minimum compatible application version"), null=True, blank=True, number_bits=[8,8,8,8])
    app_version_max = VersionField(verbose_name=_("Maximum compatible application version"), null=True, blank=True, number_bits=[8,8,8,8])
    tags = TaggableManager(blank=True, verbose_name=_("tags"))
    num_votes = models.PositiveIntegerField(default=0)
    votes = VotableManager(extra_field='num_votes')

    def get_tags(self):
        return ", ".join([tag.name for tag in self.tags.all()])

    def get_app_versions(self):
        if not self.app_version_min and not self.app_version_max:
            return pgettext_lazy("application version", "any")
        if self.app_version_min and not self.app_version_max:
            return pgettext_lazy("application version", ">= {}").format(self.app_version_min)
        if not self.app_version_min and self.app_version_max:
            return pgettext_lazy("application version", "<= {}").format(self.app_version_max)
        return pgettext_lazy("application version", ">= {0} and <= {1}").format(self.app_version_min, self.app_version_max)

    def get_filename(self):
        return basename(self.data.name)

    def get_comments_count(self):
        ct = ContentType.objects.get_for_model(Asset)
        return Comment.objects.filter(content_type=ct, object_pk=self.pk).count()

    def __str__(self):
        result = ""
        if self.application:
            result += str(self.application) + " "
        if self.component:
            result += self.component.title + " "
        result += self.title
        return result

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(User, blank=True, related_name="follower")

    def get_rating(self):
        return Asset.objects.filter(author=self.user).aggregate(Sum('num_votes'))['num_votes__sum']

    def does_follow(self, name):
        return self.follows.filter(username=name).exists()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        instance.profile = Profile.objects.create(user=instance)

