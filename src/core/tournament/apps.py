from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TournamentConfig(AppConfig):
    name = "core.tournament"
    verbose_name = _("Tournament")
