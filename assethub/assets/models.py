from __future__ import unicode_literals

from os.path import basename, join, splitext
from glob import fnmatch
from hashlib import sha1

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django_comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils import timezone

from taggit_autosuggest.managers import TaggableManager
from vote.managers import VotableManager
from versionfield import VersionField

from assets.thumbnailers import get_thumbnailer_classes, get_default_thumbnailer, get_thumbnailer

def get_api_group_name():
    # TODO: this should be configurable
    return "API Access"

def get_path(prefix, instance, filename):
    name,ext = splitext(filename)
    hash = sha1(str(timezone.now())).hexdigest()[:6]
    filename = '{}_{}{}'.format(name, hash, ext)
    return join(prefix, filename)

def get_thumbnail_path(instance, filename):
    return get_path('thumbnails/', instance, filename)

def get_data_path(instance, filename):
    return get_path('data/', instance, filename)

def get_logo_path(instance, filename):
    return get_path('logos/', instance, filename)

class Application(models.Model):
    class Meta:
        verbose_name = _("application")
        verbose_name_plural = _("applications")

    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255, verbose_name=_("title"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"))
    logo = models.ImageField(upload_to=get_logo_path, null=True, blank=True, verbose_name=_("application logo"))
    url = models.URLField(null=True, blank=True, verbose_name=_("URL"))

    def __str__(self):
        return self.title.encode('utf-8')

    def __unicode__(self):
        return self.title

class Component(models.Model):
    class Meta:
        verbose_name = _("component")
        verbose_name_plural = _("components")
        
    application = models.ForeignKey('Application', on_delete=models.CASCADE, verbose_name=_("application"))
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255, verbose_name=_("title"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("notes"))
    upload_instructions = models.TextField(null=True, blank=True, verbose_name=_("Upload instructions"))
    install_instructions = models.TextField(null=True, blank=True, verbose_name=_("Installation instructions"))
    thumbnailer_name = models.CharField(max_length=64, choices=get_thumbnailer_classes(), default=get_default_thumbnailer(), null=True, blank=True, verbose_name=_("automatic thumbnail creation"))
    thumbnail_mandatory = models.BooleanField(pgettext_lazy("component field label", "Thumbnail is mandatory"), default=False)
    file_masks = models.CharField(_("Allowed file masks"), help_text=_("space-separated list of file masks, e.g. *.jpg"), max_length=64, default="*")

    def thumbnailer(self):
        return get_thumbnailer(self.thumbnailer_name)

    def is_filename_allowed(self, name):
        if not self.file_masks:
            #print "masks not specified for component"
            return True
        for mask in self.file_masks.split():
            if fnmatch.fnmatch(name, mask):
                #print "{} matches to {}".format(name, mask)
                return True
        return False

    def __str__(self):
        return pgettext_lazy("component title", "{0} {1}").format(self.application.title, self.title).encode('utf-8')

    def __unicode__(self):
        return pgettext_lazy("component title", "{0} {1}").format(self.application.title, self.title)

class License(models.Model):
    class Meta:
        verbose_name = _("license")
        verbose_name_plural = _("licenses")
        
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))
    text = models.TextField(null=True, blank=True, verbose_name=_("Legal text"))

    def __str__(self):
        return pgettext_lazy("license title", "{0}: {1}").format(self.slug, self.title).encode('utf-8')

    def __str__(self):
        return pgettext_lazy("license title", "{0}: {1}").format(self.slug, self.title)


class Asset(models.Model):
    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("author"))
    application = models.ForeignKey('Application', on_delete=models.CASCADE, verbose_name=_("application"))
    component = models.ForeignKey('Component', on_delete=models.CASCADE, null=True, verbose_name=_("component"))
    license = models.ForeignKey('License', on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("license"))
    original_author = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("original author"))
    creation_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Originally created"))
    title = models.CharField(max_length=255, verbose_name=_("title"))
    notes = models.TextField(null=True, verbose_name=_("description"))
    image = models.ImageField(upload_to=get_thumbnail_path, verbose_name=_("thumbnail"), null=True, blank=True)
    data = models.FileField(upload_to=get_data_path, verbose_name=_("data file"))
    url = models.URLField(null=True, blank=True, verbose_name=_("URL"))
    pub_date = models.DateTimeField(verbose_name=_("date published"))
    version = VersionField(null=True, blank=True, number_bits=[8,8,8,8], verbose_name=_("asset version"))
    app_version_min = VersionField(verbose_name=_("Minimum compatible application version"), null=True, blank=True, number_bits=[8,8,8,8])
    app_version_max = VersionField(verbose_name=_("Maximum compatible application version"), null=True, blank=True, number_bits=[8,8,8,8])
    tags = TaggableManager(blank=True, verbose_name=_("tags"))
    num_votes = models.PositiveIntegerField(default=0)
    votes = VotableManager(extra_field='num_votes')

    def clean(self):
        if self.component and self.data and not self.component.is_filename_allowed(self.data.name):
            raise ValidationError(_("It is not allowed to upload files of this type for this component"))

        if self.component and self.component.thumbnail_mandatory:
            if not self.image and not (self.component and self.component.thumbnailer_name):
                raise ValidationError(_("You should upload thumbnail file"))

        super(Asset, self).clean()

    def save(self, *args, **kwargs):
        if self.data and not self.image and self.component and self.component.thumbnailer_name:
            thumbnailer = self.component.thumbnailer()
            if thumbnailer:
                thumbnail = thumbnailer.make_thumbnail(self.data)
                if thumbnail:
                    # pass save=False because otherwise it would call save() recursively
                    self.image.save("auto_thumbnail.png", thumbnail, save=False)
        super(Asset,self).save(*args, **kwargs)

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
        return result.encode('utf-8')

    def __unicode__(self):
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
    enable_api = models.BooleanField(_("Enable API"), default=False)

    def get_rating(self):
        return Asset.objects.filter(author=self.user).aggregate(Sum('num_votes'))['num_votes__sum']

    def does_follow(self, name):
        return self.follows.filter(username=name).exists()

    def enable_api_usage(self, rawpassword):
        self.enable_api = True
        self.save()
        self.user.set_password(rawpassword)
        api_group = Group.objects.get(name=get_api_group_name())
        self.user.groups.add(api_group)
        self.user.save()
    
    def is_api_enabled(self):
        return self.user.has_usable_password() and \
                self.enable_api == True and \
                self.user.groups.filter(name=get_api_group_name()).exists()

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

