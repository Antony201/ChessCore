import factory.fuzzy

from factory.django import DjangoModelFactory

from core.tournament.models import TimeControlType


class TimeControlTypeFactory(DjangoModelFactory):
    name = factory.Faker("isbn13")
    time = factory.Faker("random_int")
    additional_time = factory.Faker("random_int")

    class Meta:
        model = TimeControlType
