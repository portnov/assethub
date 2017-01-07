#!/usr/bin/env python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assethub.settings")

import django
django.setup()

from django.contrib.auth.models import User

password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
name = os.environ.get("DJANGO_SUPERUSER_NAME", "root")

try:
    root = User.objects.get(username=name)
    print "Superuser already exists: {}".format(root)
except User.DoesNotExist:
    root = User.objects.create_superuser(name, email, password)
    print "Created a superuser: {}".format(root)

