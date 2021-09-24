import factory.fuzzy

from factory.django import DjangoModelFactory

from core.tournament.models import Tournament
from tests.factories.tournament.draw_type import DrawTypeFactory
from tests.factories.tournament.time_control_type import TimeControlTypeFactory
from tests.factories.tournament.tournament_type import TournamentTypeFactory


class TournamentFactory(DjangoModelFactory):
    name = factory.Faker("isbn13")
    short_description = factory.Faker("word")
    description = factory.Faker("word")
    tournament_type = factory.SubFactory(TournamentTypeFactory)
    draw_type = factory.SubFactory(DrawTypeFactory)
    time_control_type = factory.SubFactory(TimeControlTypeFactory)

    class Meta:
        model = Tournament
