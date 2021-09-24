import math
import os

from PIL import Image as img

from django.db.models import (
    signals,
    FileField
)

from django_paranoid.models import ParanoidModel

from config.settings.base import MEDIA_ROOT
from config.settings.base import SIZES_IMAGE


class Image(ParanoidModel):
    image = FileField()
    image50 = FileField(blank=True, default="")
    image200 = FileField(blank=True, default="")
    image1000 = FileField(blank=True, default="")
    image2000 = FileField(blank=True, default="")

    @classmethod
    def resize_image(cls, sender, instance, *args, **kwargs):
        instance.image.open()

        for size in SIZES_IMAGE:
            img_name = instance._get_image_name(size)
            instance.resize(size, img_name)
            setattr(instance, f"image{size}", img_name)

    def resize(self, size, name):
        im = self.get_image(size)
        media = MEDIA_ROOT + "/"
        im.thumbnail((size, size))
        im.save(media + name)

    def get_image(self, size):
        image = img.open(self.image)
        width, height = image.size

        if (size > width) and (size > height):
            coef = math.ceil(size / max(image.size))
            image = image.resize((width * coef, height * coef))

        return image

    def _get_image_name(self, pre):
        image_name, ext = os.path.splitext(self.image.name)
        return f"{image_name}{pre}{ext}"


signals.pre_save.connect(Image.resize_image, sender=Image)
