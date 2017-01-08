
from PIL import Image
from StringIO import StringIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.module_loading import import_string

class Thumbnailer(object):
    def make_thumbnail(self, field_file):
        """This method should take a Django's FieldFile object
        (from Asset's data field) and return python file-like object
        to be saved into thumbnail field."""
        raise NotImplementedError("Abstract method")

class ImageThumbnailer(Thumbnailer):
    def make_thumbnail(self, field_file):
        img = Image.open(field_file)
        size = 128, 128
        img.thumbnail(size)
        output = StringIO()
        img.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        return ContentFile(contents)

def get_thumbnailer_classes():
    names = getattr(settings, "THUMBNAILER_CLASSES", [])
    return [(name, name) for name in names]

def get_default_thumbnailer():
    name = getattr(settings, "DEFAULT_THUMBNAILER", None)
    return name

def get_thumbnailer(name):
    if not name:
        return None
    cls = import_string(name)
    thumbnailer = cls()
    if not isinstance(thumbnailer, Thumbnailer):
        raise ValueError("Class {} is not a Thumbnailer!".format(name))
    return thumbnailer

