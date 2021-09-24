import pytest
from django.test import RequestFactory

from core.users.api.views import UserViewSet
from core.users.models import User

pytestmark = pytest.mark.django_db


class TestUserViewSet:
    def test_get_queryset(self, user: User, rf: RequestFactory):
        view = UserViewSet()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, rf: RequestFactory):
        view = UserViewSet()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)
        assert response.data == {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "city": user.city,
            "avatar": None,
            "description": user.description,
            "role": user.role,
            "manager": user.manager,
            "admin": user.admin,
            "user": user.user
        }
