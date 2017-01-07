from django.contrib.flatpages.models import FlatPage
from modeltranslation.translator import translator, TranslationOptions

from assets.models import Application, Component

class ApplicationTranslationOptions(TranslationOptions):
    fields = ('title', 'notes',)

class ComponentTranslationOptions(TranslationOptions):
    fields = ('title', 'notes', 'upload_instructions', 'install_instructions')

class FlatPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

translator.register(Application, ApplicationTranslationOptions)
translator.register(Component, ComponentTranslationOptions)
translator.register(FlatPage, FlatPageTranslationOptions)

