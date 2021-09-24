from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django_paranoid.models import ParanoidModel

User = get_user_model()


class TournamentType(ParanoidModel):
    """
    Типы турниров
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DrawType(ParanoidModel):
    """
    Типы жеребьёвок
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TimeControlType(ParanoidModel):
    """
    Типы контроля времени
    """

    name = models.CharField(max_length=255)
    time = models.IntegerField(null=True, blank=True)
    additional_time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Tournament(ParanoidModel):
    """
    Турниры
    """

    name = models.CharField(max_length=255)
    short_description = models.TextField()
    description = models.TextField()
    start_at = models.DateTimeField(null=True, blank=True)
    tournament_type = models.ForeignKey(
        TournamentType, on_delete=models.SET_NULL, related_name="tournaments", null=True
    )
    draw_type = models.ForeignKey(
        DrawType, on_delete=models.SET_NULL, related_name="tournaments", null=True
    )
    time_control_type = models.ForeignKey(
        TimeControlType,
        on_delete=models.SET_NULL,
        related_name="tournaments",
        null=True,
    )
    finished = models.BooleanField(default=False)

    @property
    def tours_amount(self) -> int:
        """
        Количество туров
        """
        return self.tours.count()

    @property
    def members_amount(self) -> int:
        """
        Количество участников этого турнира
        """
        players = set()
        for tour in self.tours.all():
            players |= tour.get_players_ids()

        return len(players)

    def __str__(self):
        return self.name


class Tour(ParanoidModel):
    """
    Туры
    """

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="tours"
    )
    start_at = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(null=True, blank=True)

    def get_players_ids(self) -> set:
        """
        Список участников тура
        """
        players = set()

        for match in self.matches.values("first_player_id", "second_player_id"):
            players.add(match["first_player_id"])
            players.add(match["second_player_id"])

        return players

    def get_players_points(self):
        """
        Очки игроков в туре
        """
        player_points = list()
        for player in self.get_players_ids():
            points = sum(
                [
                    match.get_player_point(player)
                    for match in Match.objects.filter(
                        Q(first_player_id=player) | Q(second_player=player), tour=self
                    )
                ]
            )
            player_points.append(
                {
                    "username": User.objects.get(id=player).get_full_name(),
                    "point": points,
                }
            )

        return player_points


class Match(ParanoidModel):
    """
    Игры
    """

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="matches")
    start_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    first_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="first_player_matches",
    )
    second_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="second_player_matches",
    )
    broadcast = models.BooleanField(null=True, blank=True)
    games = models.ManyToManyField("api.Game", related_name="matches")
    parent_match = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def tournament(self) -> Tournament:
        return self.tour.tournament

    def get_player_point(self, user_id: int) -> float:
        """
        Заработанные очки игрока в этой игре
        """
        user_point = float()
        for game in self.games.all():
            player_color = game.check_white_or_black(user_id)
            if player_color:
                point = getattr(game, f"{player_color}_player_points")
                user_point += point if point else 0
        return user_point
