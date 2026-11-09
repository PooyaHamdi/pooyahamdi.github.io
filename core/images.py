"""Shrink uploaded photos so the public site loads quickly.

Photos straight from a phone or camera are often 3-6 MB. The site never shows
them wider than about 500px, so anything above MAX_SIZE on the long side is
scaled down and re-saved as a compressed JPEG (PNGs stay PNG).
"""
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from PIL import Image, ImageOps

MAX_SIZE = 1600
JPEG_QUALITY = 82


def shrink(data):
    """Return smaller image bytes, or None if the image is already small enough."""
    img = Image.open(BytesIO(data))
    fmt = (img.format or "JPEG").upper()
    oriented = ImageOps.exif_transpose(img)  # bake in phone rotation before EXIF is dropped
    if max(oriented.size) <= MAX_SIZE and oriented is img and len(data) < 500_000:
        return None
    oriented.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    out = BytesIO()
    if fmt == "PNG":
        oriented.save(out, "PNG", optimize=True)
    else:
        oriented.convert("RGB").save(out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    result = out.getvalue()
    return result if len(result) < len(data) else None


def _shrink_new_uploads(sender, instance, raw=False, **kwargs):
    if raw or sender._meta.app_label != "core":
        return
    for field in sender._meta.get_fields():
        if not isinstance(field, models.ImageField):
            continue
        file = getattr(instance, field.attname)
        if not file or file._committed:  # only files being uploaded right now
            continue
        file.seek(0)
        smaller = shrink(file.read())
        file.seek(0)
        if smaller is not None:
            file.save(file.name, ContentFile(smaller), save=False)


pre_save.connect(_shrink_new_uploads, dispatch_uid="core-shrink-images")
