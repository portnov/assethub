from __future__ import unicode_literals

from os.path import basename, join, splitext
from glob import fnmatch
from hashlib import sha1
import re

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments.models import Comment
#from django.contrib.sites import get_current_site
from django.utils.translation import ugettext_lazy as _, pgettext_lazy, ugettext
from django.utils import timezone
from django.template import loader

from taggit_autosuggest.managers import TaggableManager
from vote.managers import VotableManager
from versionfield import VersionField
from notifications.signals import notify

from assets.thumbnailers import get_thumbnailer_classes, get_default_thumbnailer, get_thumbnailer, thumbnail_from_big_image

mention_re = re.compile(r'^@([-\w]+)')

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

def get_big_image_path(instance, filename):
    return get_path('bigimages/', instance, filename)

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
    max_thumbnail_size = models.IntegerField(verbose_name=_("Maximum thumbnail size"), default=settings.DEFAULT_MAX_THUMB_SIZE)
    big_image_allowed = models.BooleanField(pgettext_lazy("component field label", "Big images are allowed"), default=True)
    max_big_image_size = models.IntegerField(verbose_name=_("Maximum larger image size"), default=settings.DEFAULT_MAX_IMAGE_SIZE)
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
    big_image = models.ImageField(upload_to=get_big_image_path, verbose_name=_("larger image"), null=True, blank=True)
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

        if self.component and not self.component.big_image_allowed:
            if self.big_image:
                raise ValidationError(_("It is not allowed to upload big images for this component"))

        if self.component and self.component.thumbnail_mandatory:
            if not self.image and not (self.component and self.component.thumbnailer_name):
                raise ValidationError(_("You should upload thumbnail file"))

        super(Asset, self).clean()

    def save(self, *args, **kwargs):
        if self.data and not self.image and self.component:
            thumbnailer = self.component.thumbnailer()
            auto_thumbnail = None
            if thumbnailer:
                auto_thumbnail = thumbnailer.make_thumbnail(self.data)
            elif self.big_image:
                auto_thumbnail = thumbnail_from_big_image(self.big_image, size=self.component.max_thumbnail_size)
            if auto_thumbnail:
                # pass save=False because otherwise it would call save() recursively
                self.image.save("auto_thumbnail.png", auto_thumbnail, save=False)

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
    email_comments = models.BooleanField(_("Send email notifications about comments for my assets"), default=False)
    email_assets = models.BooleanField(_("Send email notifications about new assets in my feed"), default=False)
    email_mention = models.BooleanField(_("Send email notifications about me being mentioned"), default=False)

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

def find_mentions(text):
    if not text:
        return []
    result = []
    for word in text.split():
        match = mention_re.match(word)
        if match:
            name = match.group(1)
            try:
                user = User.objects.get(username=name)
                result.append(user)
            except User.DoesNotExist:
                pass
    return result

def notify_by_mentions(instance, text):
    for user in find_mentions(text):
        notify.send(instance, verb='mentioned', recipient=user)

### Signal handlers

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

@receiver(post_save, sender=Comment)
def on_comment_posted(sender, instance, created, **kwargs):
    comment = instance
    print("on_comment_posted: instance={}, created={}".format(instance, created))
    if created:
        print("Comment was posted for: {}".format(comment.content_object))
        # Comment posted for asset
        if comment.user == comment.content_object.author:
            print("Dont notify the author")
        else:
            notify.send(comment, verb='was posted', recipient=comment.content_object.author)
    notify_by_mentions(comment, comment.comment)

@receiver(post_save, sender=Asset)
def on_asset_posted(sender, instance, created, **kwargs):
    print("on_asset_posted: instance={}, created={}".format(instance, created))
    asset = instance
    if created:
        verb = 'was posted'
        print("New asset was posted: {}".format(asset))
    else:
        verb = 'was updated'
    print(dir(asset.author))
    for profile in asset.author.follower.all():
        notify.send(asset, verb=verb, recipient=profile.user)
    notify_by_mentions(asset, asset.notes)

@receiver(notify)
def on_notify(verb, recipient, sender, **kwargs):
    print("Notify {0} about {1} {2}".format(recipient.email, sender, verb))
    subject = None
    body = None
    template = None
    if isinstance(sender, Comment):
        comment = sender
        asset = sender.content_object
        if verb == 'was posted' and recipient.profile.email_comments:
            subject = ugettext("[{site}]: New comment posted on {asset}").format(site = comment.site.name, asset = asset)
            template = loader.get_template('assets/notification/new_comment_posted.txt')
        elif verb == 'mentioned' and recipient.profile.email_mention:
            subject = ugettext("[{site}]: You were mentioned").format(site = comment.site.name)
            template = loader.get_template('assets/notification/mention.txt')
        if template:
            context = dict(comment=comment, asset=asset, user=recipient)
            body = template.render(context)

    if isinstance(sender, Asset):
        asset = sender
        if verb == 'was posted' and recipient.profile.email_assets:
            subject = ugettext("[{site}]: New asset posted: {asset}").format(site = Site.objects.get_current(), asset = asset)
            template = loader.get_template('assets/notification/new_asset_posted.txt')
        elif verb == 'was updated' and recipient.profile.email_assets:
            subject = ugettext("[{site}]: Asset updated: {asset}").format(site = Site.objects.get_current(), asset = asset)
            template = loader.get_template('assets/notification/asset_updated.txt')
        elif verb == 'mentioned' and recipient.profile.email_mention:
            subject = ugettext("[{site}]: You were mentioned").format(site = comment.site.name)
            template = loader.get_template('assets/notification/mention.txt')
        if template:
            context = dict(asset=asset, user=recipient)
            body = template.render(context)

    if subject and body:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient.email], fail_silently = False)

