from datetime import datetime

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from core.tournament.views.tour import TourViewSet
from core.users.models import User
from tests.factories.tournament.tour import TourFactory
from tests.factories.tournament.tournament import TournamentFactory


@pytest.mark.django_db
class TestTourView:
    def setup(self) -> None:
        self.tournament = TournamentFactory.create()
        self.tour = TourFactory.create(tournament=self.tournament, finished=False)

    def test_tour_permissions_fail(self, rf: RequestFactory, user: User) -> None:
        req = rf.get("")
        force_authenticate(req, user)
        resp = TourViewSet.as_view({"get": "list"})(req)
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {"tournament": self.tournament.pk, "start_at": date, "finished": False}

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.post("", data=data)
        force_authenticate(req, user)
        resp = TourViewSet.as_view({"post": "create"})(req)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.put("", data=data, content_type="application/json")
        force_authenticate(req, user)
        resp = TourViewSet.as_view({"put": "update"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.delete("")
        force_authenticate(req, user)
        resp = TourViewSet.as_view({"delete": "destroy"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_tour_list(self, rf: RequestFactory, admin: User) -> None:
        req = rf.get("")
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"get": "list"})(req)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["results"][0]["id"] == self.tour.pk

    def test_tour_create(self, rf: RequestFactory, admin: User) -> None:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        req = rf.post(
            "",
            data={
                "tournament": self.tournament.pk,
                "start_at": date,
                "finished": False,
            },
        )
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"post": "create"})(req)

        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["tournament"] == self.tournament.pk

    def test_tour_update(self, rf: RequestFactory, admin: User) -> None:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        req = rf.put(
            "",
            data={
                "tournament": self.tournament.pk,
                "start_at": date,
                "finished": bool(not self.tour.finished),
            },
            content_type="application/json",
        )
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"put": "update"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["finished"] == bool(not self.tour.finished)

    def test_tour_retrieve(self, rf: RequestFactory, admin: User) -> None:
        req = rf.get("")
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"get": "retrieve"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == self.tour.pk

    def test_tour_delete(self, rf: RequestFactory, admin: User) -> None:
        req = rf.get("")
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"get": "retrieve"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == self.tour.pk

        req = rf.delete("")
        force_authenticate(req, admin)
        resp = TourViewSet.as_view({"delete": "destroy"})(req, pk=self.tour.pk)

        assert resp.status_code == status.HTTP_204_NO_CONTENT
