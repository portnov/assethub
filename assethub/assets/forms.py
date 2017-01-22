
from django import forms
from django.forms import ModelForm
from django.db import models
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext as _, ugettext_lazy as _l

from pagedown.widgets import PagedownWidget
from versionfield.forms import VersionField
from taggit_autosuggest.widgets import TagAutoSuggest
from taggit.models import Tag

from models import Asset, License, Application, Component

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['application', 'component', 'license', 'original_author', 'creation_date', 'title', 'notes', 'image', 'big_image', 'data', 'url', 'version', 'app_version_min', 'app_version_max', 'tags']
        widgets = {'notes': PagedownWidget(), 
                   'application': forms.HiddenInput(),
                   'component': forms.HiddenInput()
                  }

    def __init__(self, component, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        if component and not component.big_image_allowed:
            del self.fields['big_image']

    def clean(self):
        cleaned_data = super(AssetForm, self).clean()
        component = cleaned_data.get("component")
        image = cleaned_data.get("image")
        if not image:
            pass
        else:
           w, h = get_image_dimensions(image)
           if w > component.max_thumbnail_size or h > component.max_thumbnail_size:
               raise forms.ValidationError(_("The thumbnail is too large: {0}x{1}; maximum size allowed is {2}px").format(w,h,component.max_thumbnail_size))
        big_image = cleaned_data.get("big_image")
        if not big_image:
            pass
        else:
           w, h = get_image_dimensions(big_image)
           if w > component.max_big_image_size or h > component.max_big_image_size:
               raise forms.ValidationError(_("The image is too large: {0}x{1}; maximum size allowed is {2}px").format(w,h,component.max_big_image_size))
        return cleaned_data

class AdvancedSearchForm(forms.Form):
    application = forms.ModelChoiceField(queryset=Application.objects.all(), label=_l("Application"), required=False)
    component = forms.ModelChoiceField(queryset=Component.objects.all(), label=_l("Component"), required=False)
    license = forms.ModelChoiceField(queryset=License.objects.all(), label=_l("License"), required=False)
    author = forms.ModelChoiceField(queryset=User.objects.all(), label=_l("Author"), required=False)
    original_author = forms.CharField(label=_l("Original author"), required=False)
    title = forms.CharField(label=_l("Title"), required=False)
    tags = TagAutoSuggest(Tag)
    version = VersionField(label=_l("Asset version"), required=False)
    app_version = VersionField(label=_l("Application version"), required=False)

class SimpleSearchForm(forms.Form):
    query = forms.CharField(label=_l("Search"), required=False)

class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

