from django.core.mail import send_mail

from notifications.signals import notify
from django_comments.models import Comment

events_registry = []

class Event(object):
    model = None
    parent = None
    verb = None

    @staticmethod
    def get_email_subject(instance, parent, actor, recipient):
        raise NotImplementedError

    @staticmethod
    def get_email_body_template(instance, parent, actor, recipient):
        """Should return template name to render email body."""
        raise NotImplementedError

    @staticmethod
    def get_template_data(instance, parent, actor, recipient):
        """Should return a tuple:
        (template name, context)
        """
        raise NotImplementedError

    @staticmethod
    def is_user_subscribed(recipient):
        raise NotImplementedError

    @staticmethod
    def register(event):
        global events_registry
        events_registry.append(event)

    @staticmethod
    def get(model, parent, verb):
        global events_registry
        for event in events_registry:
            model_ok = event.model is None or model == event.model
            parent_ok = event.parent is None or parent == event.parent
            verb_ok = event.verb is None or verb == event.verb
            if model_ok and parent_ok and verb_ok:
                return event
        return None

class CommentPosted(Event):
    model = Comment
    parent = Asset
