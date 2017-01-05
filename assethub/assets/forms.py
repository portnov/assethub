
from django import forms
from django.forms import ModelForm
from django.db import models
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from pagedown.widgets import PagedownWidget

from models import Asset

MAX_IMAGE_SIZE=300

class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = ['license', 'original_author', 'creation_date', 'title', 'notes', 'image', 'data', 'url', 'version', 'app_version_min', 'app_version_max', 'tags']
        widgets = {'notes': PagedownWidget()}

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("No thumbnail provided")
        else:
           w, h = get_image_dimensions(image)
           if w > MAX_IMAGE_SIZE or h > MAX_IMAGE_SIZE:
               raise forms.ValidationError(_("The image is too large: {0}x{1}; maximum size allowed is {2}px").format(w,h,MAX_IMAGE_SIZE))
        return image

class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

