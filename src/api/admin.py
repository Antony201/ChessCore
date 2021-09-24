from django.contrib import admin

from api.forms import GameAdminForm
from api.models import (
    Game
)
from api.services import create_broadcast_for_game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    form = GameAdminForm
    readonly_fields = (
        'white_player_time_remaining',
        'black_player_time_remaining',
    )

    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        create_broadcast_for_game(obj)
