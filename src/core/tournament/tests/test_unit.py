import pytest

from core.tournament.models import Tour, Match


@pytest.mark.django_db
def test_tournaments(create_tournament, create_tour, create_match, create_player):
    tournament = create_tournament
    tour = create_tour(tournament.id)
    first_player = create_player("first player", "first_player", "email@example.com")
    second_player = create_player(
        "second player", "second_player", "email_1@example.com"
    )
    create_match(tour.id, first_player.id, second_player.id)
    assert tournament.tours_amount == 1
    assert tournament.members_amount == 2


@pytest.mark.django_db
def test_tournaments_invalid(
    create_tournament, create_tour, create_match, create_player
):
    tournament = create_tournament

    assert tournament.tours_amount == 0
    assert tournament.members_amount == 0


@pytest.mark.django_db
def test_tour_get_players_ids(
    create_tournament, create_tour, create_match, create_player
):
    tournament = create_tournament
    tour = create_tour(tournament.id)
    first_p = create_player("first player", "first_username", "email@example.com")
    second_p = create_player("second player", "second_username", "email1@example.com")
    create_match(tour.id, first_p.id, second_p.id)

    assert Tour.objects.last().get_players_ids() == {first_p.id, second_p.id}


@pytest.mark.django_db
def test_tour_get_players_points(
    create_tournament, create_tour, create_match, create_player, create_game_fix
):
    tournament = create_tournament
    tour = create_tour(tournament.id)
    first_p = create_player("first player", "first_username", "email@example.com")
    second_p = create_player("second player", "second_username", "email1@example.com")
    match = create_match(tour.id, first_p.id, second_p.id)
    game = create_game_fix((first_p, second_p))
    game.black_player_points = 5
    game.white_player_points = 4
    game.save()
    match.games.add(game)
    for i in Tour.objects.last().get_players_points():
        if i["username"] == "first player":
            assert i["point"] == 4.0
        if i["username"] == "second player":
            assert i["point"] == 5.0


@pytest.mark.django_db
def test_match_get_players_point(
    create_tournament, create_tour, create_match, create_player, create_game_fix
):
    tournament = create_tournament
    tour = create_tour(tournament.id)
    first_p = create_player("first player", "first_username", "email@example.com")
    second_p = create_player("second player", "second_username", "email1@example.com")
    match = create_match(tour.id, first_p.id, second_p.id)
    game = create_game_fix((first_p, second_p))
    game.black_player_points = 5
    game.white_player_points = 4
    game.save()
    match.games.add(game)
    assert Match.objects.last().get_player_point(second_p.id) == 5.0
