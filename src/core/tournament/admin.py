from django.contrib import admin
from django_paranoid.admin import ParanoidAdmin

from core.tournament.models import (
    Tournament,
    TournamentType,
    Match,
    Tour,
    TimeControlType,
    DrawType,
)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    pass


@admin.register(TournamentType)
class TournamentTypeAdmin(ParanoidAdmin):
    pass


@admin.register(DrawType)
class DrawTypeAdmin(ParanoidAdmin):
    pass


@admin.register(TimeControlType)
class TimeControlTypeAdmin(ParanoidAdmin):
    fields = ("id", "name", "time", "additional_time")
    readonly_fields = ("id",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    pass
