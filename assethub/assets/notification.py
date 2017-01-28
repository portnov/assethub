from os.path import join
import re

from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext
from django.template import loader

from django_comments.models import Comment
from notifications.signals import notify

from assets.models import Asset, Comment, Profile

events_registry = []
mention_re = re.compile(r'^@([-\w]+)')

print "Importing notification"

### Events framework

class EventInfo(object):
    def __init__(self):
        self.email_subject = None
        self.email_body_template = None
        self.template_name = None
        self.email_context = None
        self.verb = None
        self.is_user_subscribed = None
        self.recipients = None
        self.actor = None
        self.url = None

class Event(object):
    model = None
    parent = None
    created = None

    def __init__(self, instance, parent):
        self.instance = instance
        self.parent = parent

    def get_info(self):
        """Should return an EventInfo instance"""
        raise NotImplementedError

    @staticmethod
    def register(event):
        global events_registry
        events_registry.append(event)
        return event

    @staticmethod
    def get(instance, parent, created):
        global events_registry
        result = []
        for event in events_registry:
            model_ok = event.model is None or isinstance(instance, event.model)
            parent_ok = event.parent is None or parent is None or isinstance(parent, event.parent)
            verb_ok = event.created is None or created == event.created
            if model_ok and parent_ok and verb_ok:
                result.append(event(instance, parent).get_info())
        return result

    @staticmethod
    def process(instance, parent, created):
        for info in Event.get(instance, parent, created):
            for recipient in info.recipients:
                if recipient == info.actor:
                    continue
                print("Notify {0} about {1} {2}".format(recipient, instance, info.verb))
                notify.send(info.actor, verb=info.verb, action_object=instance, target=parent, recipient=recipient, template=info.template_name, url=info.url)
                if info.is_user_subscribed(recipient):
                    subject = info.email_subject
                    template = loader.get_template(join('assets', 'notification', info.email_body_template))
                    context = info.email_context
                    context['user'] = recipient
                    body = template.render(context)
                    if subject and body:
                        print("Send mail to {0}: {1}".format(recipient.email, subject))
                        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient.email], fail_silently = False)

### Specific events

@Event.register
class CommentPosted(Event):
    model = Comment
    parent = Asset
    created = True

    def get_info(self):
        info = EventInfo()
        info.email_subject = ugettext("[{site}]: New comment posted on {asset}").format(site = self.instance.site.name, asset = self.parent)
        info.email_body_template = 'new_comment_posted.txt'
        info.template_name = 'new_comment_posted.html'
        info.email_context = dict(comment = self.instance, asset=self.parent, author=self.instance.user)
        info.is_user_subscribed = lambda user: user.profile.email_comments
        info.recipients = [self.instance.content_object.author]
        info.verb = 'was posted'
        info.actor = self.instance.user
        info.url = get_comment_url(self.instance)
        return info

@Event.register
class CommentMention(Event):
    model = Comment
    parent = Asset
    created = None

    def get_info(self):
        info = EventInfo()
        info.email_subject = ugettext("[{site}]: You were mentioned").format(site = self.instance.site.name)
        info.email_body_template = 'comment_mention.txt'
        info.template_name = 'comment_mention.html'
        info.email_context = dict(comment=self.instance, asset=self.parent, author=self.instance.user)
        info.is_user_subscribed = lambda user: user.profile.email_mention
        info.recipients = find_mentions(self.instance.comment)
        info.verb = 'mentioned'
        info.actor = self.instance.user
        info.url = get_comment_url(self.instance)
        return info

@Event.register
class AssetPosted(Event):
    model = Asset
    parent = None
    created = True

    def get_info(self):
        info = EventInfo()
        info.email_subject = ugettext("[{site}]: New asset posted: {asset}").format(site = Site.objects.get_current(), asset = self.instance)
        info.email_body_template = 'new_asset_posted.txt'
        info.template_name = 'new_asset_posted.html'
        info.email_context = dict(asset=self.instance, author=self.instance.author)
        info.is_user_subscribed = lambda user: user.profile.email_assets
        info.recipients = [r.user for r in self.instance.author.follower.all()]
        info.verb = 'was posted'
        info.actor = self.instance.author
        info.url = get_asset_url(self.instance)
        return info

@Event.register
class AssetUpdated(Event):
    model = Asset
    parent = None
    created = False

    def get_info(self):
        info = EventInfo()
        info.email_subject = ugettext("[{site}]: Asset updated: {asset}").format(site = Site.objects.get_current(), asset = self.instance)
        info.email_body_template = 'asset_updated.txt'
        info.template_name = 'asset_updated.html'
        info.email_context = dict(asset=self.instance, author=self.instance.author)
        info.is_user_subscribed = lambda user: user.profile.email_assets
        info.recipients = [r.user for r in self.instance.author.follower.all()]
        info.verb = 'was updated'
        info.actor = self.instance.author
        info.url = get_asset_url(self.instance)
        return info

@Event.register
class AssetMention(Event):
    model = Asset
    parent = None
    created = None

    def get_info(self):
        info = EventInfo()
        info.email_subject = ugettext("[{site}]: You were mentioned").format(site = Site.objects.get_current())
        info.email_body_template = 'asset_mention.txt'
        info.template_name = 'asset_mention.html'
        info.email_context = dict(asset=self.instance, author=self.instance.author)
        info.is_user_subscribed = lambda user: user.profile.email_mention
        info.recipients = find_mentions(self.instance.notes)
        info.verb = 'mentioned'
        info.actor = self.instance.author
        info.url = get_asset_url(self.instance)
        return info

### Utils

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

def notify_by_mentions(author, instance, target, text):
    for user in find_mentions(text):
        notify.send(author, verb='mentioned', recipient=user, action_object=instance, target=target)

def get_asset_url(asset):
    return reverse('asset', args=[asset.pk])

def get_comment_url(comment):
    asset = comment.content_object
    return join(get_asset_url(asset), "#c{}".format(comment.id))

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
    asset = instance.content_object
    print("on_comment_posted: instance={}, created={}".format(instance, created))
    Event.process(comment, asset, created)

@receiver(post_save, sender=Asset)
def on_asset_posted(sender, instance, created, **kwargs):
    print("on_asset_posted: instance={}, created={}".format(instance, created))
    asset = instance
    Event.process(asset, None, created)

# @receiver(notify)
# def on_notify(verb, recipient, sender, **kwargs):
#     print("Notify {0} about {1} {2}".format(recipient.email, sender, verb))
#     subject = None
#     body = None
#     template = None
#     if isinstance(sender, Comment):
#         comment = sender
# #         asset = sender.content_object
# #         if verb == 'was posted' and recipient.profile.email_comments:
# #             subject = 
# #             template = loader.get_template('assets/notification/new_comment_posted.txt')
# #         elif verb == 'mentioned' and recipient.profile.email_mention:
# #             subject = 
# #             template = loader.get_template('assets/notification/mention.txt')
# #         if template:
# #             context = dict(comment=comment, asset=asset, user=recipient)
# #             body = template.render(context)
# 
#     if isinstance(sender, Asset):
#         asset = sender
# #         if verb == 'was posted' and recipient.profile.email_assets:
# #             subject = 
# #             template = loader.get_template('assets/notification/new_asset_posted.txt')
# #         elif verb == 'was updated' and recipient.profile.email_assets:
# #             subject = 
# #             template = loader.get_template('assets/notification/asset_updated.txt')
# #         elif verb == 'mentioned' and recipient.profile.email_mention:
# #             subject = ugettext("[{site}]: You were mentioned").format(site = comment.site.name)
# #             template = loader.get_template('assets/notification/mention.txt')
# #         if template:
# #             context = dict(asset=asset, user=recipient)
# #             body = template.render(context)
# 
#     if subject and body:
#         send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient.email], fail_silently = False)

