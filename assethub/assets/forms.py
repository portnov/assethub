
from django import forms
from django.forms import ModelForm

from models import Asset

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = ['application', 'component', 'title', 'notes', 'image', 'data', 'url', 'version', 'tags']

