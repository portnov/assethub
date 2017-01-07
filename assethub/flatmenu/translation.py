from modeltranslation.translator import translator, TranslationOptions

from flatmenu.models import MenuItem

class MenuItemTranslationOptions(TranslationOptions):
    fields = ('title', )

translator.register(MenuItem, MenuItemTranslationOptions)

