from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from pagedown.widgets import PagedownWidget

from models import Application, Component, Asset, Profile, License

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['slug', 'title', 'url', 'notes', 'logo']
        widgets = {'notes': PagedownWidget()}

class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationForm

class LicenseForm(ModelForm):
    class Meta:
        model = License
        fields = ['slug', 'title', 'notes', 'text']
        widgets = {'notes': PagedownWidget(), 'text': PagedownWidget()}

class LicenseAdmin(admin.ModelAdmin):
    form = LicenseForm

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Component)
admin.site.register(Asset)
admin.site.register(License, LicenseAdmin)

