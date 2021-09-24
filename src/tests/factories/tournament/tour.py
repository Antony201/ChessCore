import factory.fuzzy
from factory.django import DjangoModelFactory

from core.tournament.models import Tour
from tests.factories.tournament.tournament import TournamentFactory


class TourFactory(DjangoModelFactory):
    tournament = factory.SubFactory(TournamentFactory)

    class Meta:
        model = Tour
