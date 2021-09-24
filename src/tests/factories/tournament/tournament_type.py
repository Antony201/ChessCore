import factory.fuzzy

from factory.django import DjangoModelFactory

from core.tournament.models import TournamentType


class TournamentTypeFactory(DjangoModelFactory):
    name = factory.Faker("isbn13")

    class Meta:
        model = TournamentType
