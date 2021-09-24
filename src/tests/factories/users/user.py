import factory.fuzzy

from factory.django import DjangoModelFactory

from core.users.models import User


class UserFactory(DjangoModelFactory):
    email = factory.Faker("email")
    username = factory.Faker("user_name")
    password = factory.Faker("password")

    class Meta:
        model = User
