from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin

from pagedown.widgets import PagedownWidget
from modeltranslation.admin import TranslationAdmin

from models import Application, Component, Asset, Profile, License
import assets.translation

class ComponentInline(admin.StackedInline):
    model = Component

class ComponentAdmin(TranslationAdmin):
    pass

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

class ApplicationAdmin(TranslationAdmin):
    form = ApplicationForm
    #inlines = [ComponentInline]

class LicenseForm(ModelForm):
    class Meta:
        model = License
        fields = ['slug', 'title', 'notes', 'text']
        widgets = {'notes': PagedownWidget(), 'text': PagedownWidget()}

class LicenseAdmin(admin.ModelAdmin):
    form = LicenseForm

class TranslatedFlatPageAdmin(FlatPageAdmin, TranslationAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(TranslatedFlatPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        self.patch_translation_field(db_field, field, **kwargs)
        return field

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Asset)
admin.site.register(License, LicenseAdmin)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TranslatedFlatPageAdmin)

