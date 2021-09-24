import factory.fuzzy

from factory.django import DjangoModelFactory

from core.tournament.models import DrawType


class DrawTypeFactory(DjangoModelFactory):
    name = factory.Faker("isbn13")

    class Meta:
        model = DrawType
