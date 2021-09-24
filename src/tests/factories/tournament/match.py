import factory.fuzzy
from factory.django import DjangoModelFactory

from core.tournament.models import Match
from tests.factories.tournament.tour import TourFactory


class MatchFactory(DjangoModelFactory):
    tour = factory.SubFactory(TourFactory)

    class Meta:
        model = Match
