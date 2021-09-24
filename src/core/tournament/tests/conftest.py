from datetime import datetime

import pytest

from api.services import create_game
from core.tournament.models import Tournament, TournamentType, Tour, Match
from core.users.models import User


@pytest.fixture
def create_tournament_type():
    return TournamentType.objects.create(name="test_type")


@pytest.fixture
def create_tournament(create_tournament_type):
    return Tournament.objects.create(
        name="test",
        short_description="test short desc",
        description="test desc",
        tournament_type=create_tournament_type,
        start_at=datetime.now(),
    )


@pytest.fixture
def create_tour():
    def create(tournament_id: int):
        return Tour.objects.create(tournament_id=tournament_id, start_at=datetime.now())

    return create


@pytest.fixture
def create_match():
    def create(tour_id: int, first_player_id: int, second_player_id: int):
        return Match.objects.create(
            tour_id=tour_id,
            start_at=datetime.now(),
            first_player_id=first_player_id,
            second_player_id=second_player_id,
        )

    return create


@pytest.fixture
def create_player():
    def create(
        name: str,
        username: str,
        email: str,
    ):
        return User.objects.create(first_name=name, username=username, email=email)

    return create


@pytest.fixture
def create_game_fix():
    def create(users):
        player, opponent = users
        return create_game(
            {},
            {},
            white_player=player,
            black_player=opponent,
        )

    return create
