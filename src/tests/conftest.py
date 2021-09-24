import pytest
from django.test import Client
from rest_framework.test import APIClient

from tests.factories.users.user import UserFactory


@pytest.fixture
def user():
    user = UserFactory()
    return user


@pytest.fixture
def staff(user):
    user.is_staff = True

    user.save()

    return user


@pytest.fixture
def admin(user):
    user.is_staff = True
    user.is_superuser = True

    user.save()

    return user


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(admin):
    client = Client()
    client.force_login(admin)
    return client


@pytest.fixture
def user_api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def admin_api_client(admin):
    client = APIClient()
    client.force_authenticate(admin)
    return client
