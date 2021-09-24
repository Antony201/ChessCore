import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from core.tournament.views.tournament import TournamentViewSet
from tests.factories.tournament.tournament import TournamentFactory


@pytest.mark.django_db
class TestTournamentView:
    def setup(self):
        self.tournament = TournamentFactory.create()

    def test_tournament_list_success(self, rf, user):
        req = rf.get("")
        force_authenticate(req, user)
        resp = TournamentViewSet.as_view({"get": "list"})(req)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["results"][0]["id"] == self.tournament.pk
