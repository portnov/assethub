from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from taggit_autosuggest.managers import TaggableManager
from vote.managers import VotableManager

from django.contrib.auth.models import User

class Application(models.Model):
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title

class Component(models.Model):
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.application.title + " " + self.title

class License(models.Model):
    slug = models.SlugField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{0}: {1}".format(self.slug, self.title)

class Asset(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    component = models.ForeignKey('Component', on_delete=models.CASCADE, null=True)
    license = models.ForeignKey('License', on_delete=models.SET_NULL, null=True, blank=False)
    title = models.CharField(max_length=255)
    notes = models.TextField(null=True)
    image = models.ImageField(upload_to='thumbnails/')
    data = models.FileField(upload_to='data/')
    url = models.URLField(null=True, blank=True)
    pub_date = models.DateTimeField('Published')
    version = models.CharField(max_length=10, null=True, blank=True)
    tags = TaggableManager(blank=True)
    num_votes = models.PositiveIntegerField(default=0)
    votes = VotableManager(extra_field='num_votes')

    def get_tags(self):
        return ", ".join([tag.name for tag in self.tags.all()])

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

