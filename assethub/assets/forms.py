
from django import forms
from django.forms import ModelForm
from django.db import models

from pagedown.widgets import PagedownWidget

from models import Asset

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['application', 'component', 'title', 'notes', 'image', 'data', 'url', 'version', 'tags']
        widgets = {'notes': PagedownWidget()}


