from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from flatmenu.models import MenuItem
import flatmenu.translation

class MenuItemAdmin(TranslationAdmin):
    pass

admin.site.register(MenuItem, MenuItemAdmin)

