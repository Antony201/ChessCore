from factory.django import DjangoModelFactory

from api.models import Game


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game
