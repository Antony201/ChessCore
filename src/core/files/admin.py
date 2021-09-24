from django.contrib import admin

from core.files.models.Image import Image
from django_paranoid.admin import ParanoidAdmin


class ImageAdmin(ParanoidAdmin):
    exclude = ["image50", "image200", "image1000", "image2000"]


admin.site.register(Image, ImageAdmin)
