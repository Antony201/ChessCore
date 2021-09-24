from django.contrib import admin

from core.chess.models import Slide


class SlideAdmin(admin.ModelAdmin):
    exclude = ["image50", "image200", "image1000", "image2000"]


admin.site.register(Slide, SlideAdmin)
