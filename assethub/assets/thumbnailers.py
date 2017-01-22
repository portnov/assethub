
import sys
from os.path import dirname, splitext, basename
from zipfile import ZipFile
from PIL import Image
from StringIO import StringIO
from importlib import import_module

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.module_loading import import_string
from django.core.files.images import get_image_dimensions

def import_by_path(path):
    """Import python module by path.
    Supports different forms:
    * absolute paths
    * relative paths
    * fully qualified python module names
    """
    base = settings.BASE_DIR
    if path.startswith(base):
        path = path[len(base):]
    elif path.startswith('/'):
        directory = dirname(path)
        if directory not in sys.path:
            #print("Adding {} to sys.path".format(directory))
            sys.path.append(directory)
        path = basename(path)
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('.py'):
        path, ext = splitext(path)
    path = path.replace('/', '.')
    return import_module(path)

def thumbnail_from_big_image(big_image, size=None):
    try:
        src_w, src_h = get_image_dimensions(big_image)
        img = Image.open(big_image)
        img.thumbnail((512,512))
        th_w, th_h = img.size
        if size is None:
            size = settings.DEFAULT_MAX_THUMB_SIZE
        if th_w > size or th_h > size:
            x = (th_w - size)/2.0
            if x < 0:
                x = 0
            y = (th_h - size)/2.0
            if y < 0:
                y = 0
            img = img.crop((x,y, x, y))
        output = StringIO()
        img.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        return ContentFile(contents)
    except IOError:
        return None

class Thumbnailer(object):
    title = "Abstract thumbnailer"
    def make_thumbnail(self, field_file):
        """This method should take a Django's FieldFile object
        (from Asset's data field) and return python file-like object
        to be saved into thumbnail field."""
        raise NotImplementedError("Abstract method")

class ImageThumbnailer(Thumbnailer):
    """Thumbnailer for image files.
    Supports all file format supported by Pillow.
    """

    title = "Image file thumbnailer"

    def make_thumbnail(self, field_file):
        try: 
            img = Image.open(field_file)
            size = 128, 128
            img.thumbnail(size)
            output = StringIO()
            img.save(output, format="PNG")
            contents = output.getvalue()
            output.close()
            return ContentFile(contents)
        except IOError:
            return None

class KritaPresetThumbnailer(Thumbnailer):
    """Thumbnailer for Krita brush preset files (.kpp).
    Returns the source file, since KPP is really PNG."""

    title = "Krita preset thumbnailer"

    def make_thumbnail(self, field_file):
        if not field_file.name.endswith('.kpp'):
            return None
        return field_file

class KritaBundleThumbnailer(Thumbnailer):
    """Thumbnailer for Krita resource bundle files (.bundle).
    Extracts preview.png from the bundle."""

    title = "Krita resource bundle thumbnailer"

    def make_thumbnail(self, field_file):
        if not field_file.name.endswith('.bundle'):
            return None
        zf = ZipFile(field_file, 'r')
        preview_bytes = zf.read("preview.png")
        zf.close()
        return ContentFile(preview_bytes)

def get_thumbnailer_classes():
    names = getattr(settings, "THUMBNAILER_CLASSES", [])
    result = []
    for name in names:
        cls = get_thumbnailer(name)
        if not cls:
            raise ImportError("Unknown thumbnailer class: {}".format(name))
        result.append((name, cls.title))
    return result

def get_default_thumbnailer():
    name = getattr(settings, "DEFAULT_THUMBNAILER", None)
    return name

def get_thumbnailer(name):
    if not name:
        name = get_default_thumbnailer()
    if not name:
        return None
    cls = import_string(name)
    thumbnailer = cls()
    if not isinstance(thumbnailer, Thumbnailer):
        raise ValueError("Class {} is not a Thumbnailer!".format(name))
    return thumbnailer

