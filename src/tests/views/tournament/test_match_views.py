from datetime import datetime

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from core.tournament.models import Match
from core.tournament.views.match import MatchViewSet, MatchGameViewSet
from core.users.models import User
from tests.factories.tournament.game import GameFactory
from tests.factories.tournament.match import MatchFactory
from tests.factories.tournament.tour import TourFactory
from tests.factories.users.user import UserFactory


@pytest.mark.django_db
class TestTourView:
    def setup(self) -> None:
        self.first_player = UserFactory()
        self.second_player = UserFactory()
        self.tour = TourFactory()
        self.game = GameFactory(
            white_player=self.first_player,
            black_player=self.second_player,
            broadcast_type="both",
        )
        self.match = MatchFactory(
            tour=self.tour,
            first_player=self.first_player,
            second_player=self.second_player,
        )

        self.match.games.add(self.game)
        self.match.save()

    def test_match_permissions_fail(self, rf: RequestFactory, user: User) -> None:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        game = GameFactory(
            white_player=self.second_player,
            black_player=self.first_player,
            broadcast_type="both",
        )
        data = {
            "start_at": date,
            "broadcast": True,
            "tour": self.tour.pk,
            "first_player": self.first_player.pk,
            "second_player": self.second_player.pk,
            "games": [game.pk],
        }
        req = rf.post(
            "",
            data=data,
        )
        force_authenticate(req, user)
        resp = MatchViewSet.as_view({"post": "create"})(req)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.put(
            "",
            data=data,
            content_type="application/json",
        )
        force_authenticate(req, user)
        resp = MatchViewSet.as_view({"put": "update"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.delete("")
        force_authenticate(req, user)

        resp = MatchViewSet.as_view({"delete": "destroy"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_match_create(self, rf: RequestFactory, admin: User) -> None:
        game = GameFactory(
            white_player=self.first_player,
            black_player=self.second_player,
            broadcast_type="both",
        )
        data = {
            "start_at": "2021-03-29T18:40:42.791Z",
            "broadcast": True,
            "tour": self.tour.pk,
            "first_player": self.first_player.pk,
            "second_player": self.second_player.pk,
            "parent_match": self.match.pk,
            "games": [game.pk],
        }
        req = rf.post(
            "",
            data=data,
        )
        force_authenticate(req, admin)
        resp = MatchViewSet.as_view({"post": "create"})(req)

        assert resp.status_code == status.HTTP_201_CREATED

    def test_match_update(self, rf: RequestFactory, admin: User) -> None:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        game = GameFactory(
            white_player=self.second_player,
            black_player=self.first_player,
            broadcast_type="both",
        )
        data = {
            "start_at": date,
            "broadcast": True,
            "tour": self.tour.pk,
            "first_player": self.first_player.pk,
            "second_player": self.second_player.pk,
            "games": [game.pk],
        }
        req = rf.put(
            "",
            data=data,
            content_type="application/json",
        )
        force_authenticate(req, admin)
        resp = MatchViewSet.as_view({"put": "update"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_200_OK

    def test_match_destroy(self, rf: RequestFactory, admin: User) -> None:
        req = rf.delete("")
        force_authenticate(req, admin)

        match = Match.objects.get(pk=self.match.pk)

        assert match

        resp = MatchViewSet.as_view({"delete": "destroy"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_match_game_permissions_fail(self, rf: RequestFactory, user: User) -> None:
        req = rf.post("", data={
            "white_player": self.first_player.pk,
            "black_player": self.second_player.pk
        })
        force_authenticate(req, user)

        resp = MatchGameViewSet.as_view({"post": "create"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

        req = rf.delete("")
        force_authenticate(req, user)

        resp = MatchGameViewSet.as_view({"delete": "destroy"})(req, pk=self.match.pk, game=self.game.uuid)

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_match_game_create(self, rf: RequestFactory, admin: User) -> None:
        req = rf.post("", data={
            "white_player": self.first_player.pk,
            "black_player": self.second_player.pk
        })
        force_authenticate(req, admin)

        resp = MatchGameViewSet.as_view({"post": "create"})(req, pk=self.match.pk)

        assert resp.status_code == status.HTTP_201_CREATED

    def test_match_game_delete(self, rf: RequestFactory, admin: User) -> None:
        req = rf.delete("")
        force_authenticate(req, admin)

        resp = MatchGameViewSet.as_view({"delete": "destroy"})(req, pk=self.match.pk, game=self.game.uuid)

        assert resp.status_code == status.HTTP_204_NO_CONTENT


