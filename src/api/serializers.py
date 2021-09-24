from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken
)
from six import text_type

from core.files.serializers import ImageSerializer
from . import services
from .models import Board, Elo, Game, Result, Move
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


class EloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elo
        fields = (
            "rating",
            "previous_rating",
            "wins",
            "losses",
            "draws",
            "uuid",
        )


class UserEloSerializer(serializers.ModelSerializer):
    elo = EloSerializer()
    id = serializers.IntegerField()
    avatar = ImageSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "active",
            "elo",
            "first_name",
            "last_name",
            "avatar"
        )


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            "fen",
            "board_fen",
            "board_fen_flipped",
            "updated_at",
            "game_uuid",
        )


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = (
            "result",
            "termination",
        )


class GameSerializer(serializers.ModelSerializer):
    black_player = UserEloSerializer(required=False)
    white_player = UserEloSerializer(required=False)
    board = BoardSerializer(required=False)
    result = ResultSerializer(required=False)
    pgn = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "uuid",
            "black_player",
            "white_player",
            "created_at",
            "started_at",
            "finished_at",
            "result",
            "board",
            "black_player_broadcast",
            "white_player_broadcast",
            "black_player_broadcast_board",
            "white_player_broadcast_board",
            "black_player_can_claim_draw",
            "white_player_can_claim_draw",
            'pgn',
            'time_control_type',
            'broadcast_type',
            'white_player_time_remaining',
            'black_player_time_remaining',
        )

    # TODO временно убрали логику проверок пользователя, так как не ясно как в сокетах брать пользователя
    # def get_black_player_broadcast_board(self, obj):
    #     if self.context.get('request'):
    #         auth_username = self.context["request"].user
    #         return self._get_broadcast_board(obj, 'black', auth_username)
    #
    # def get_white_player_broadcast_board(self, obj):
    #     if self.context.get('request'):
    #         auth_username = self.context["request"].user
    #         return self._get_broadcast_board(obj, 'white', auth_username)
    #
    # def _get_broadcast_board(
    #     self, game: Game, color: str, user
    # ):
    #     if user.is_staff:
    #         return getattr(game, f'{color}_player_broadcast_board')
    #     user_color = game.check_white_or_black(user.id)
    #     if color != user_color:
    #         return None
    #     return getattr(game, f'{user_color}_player_broadcast_board')

    def get_pgn(self, obj):
        from .services import get_pgn_game_from_uuid
        return str(get_pgn_game_from_uuid(obj.uuid))

    def create(self, validated_data):
        result_data = validated_data.pop("result", {})
        board_data = validated_data.pop("board", {})

        preferred_color = self.context["request"].data.get("preferred_color", "random")

        auth_username = self.context["request"].user

        game = services.create_game(
            result_data=result_data, board_data=board_data, **validated_data
        )

        services.assign_color(game, auth_username, preferred_color)

        return game


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['refresh'] = text_type(refresh)

        if self.user.is_superuser:
            new_token = refresh.access_token
            new_token.set_exp(lifetime=timedelta(days=360))
            data['access'] = text_type(new_token)
        else:
            data['access'] = text_type(refresh.access_token)

        data["name"] = self.user.username
        data["active"] = self.user.active
        data['user_id'] = self.user.id
        data['expires_in'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds
        self.clean_old_session(str(data['refresh']))
        return data

    def clean_old_session(self, new):
        """
        Clean all old session except new
        """
        old_tokens = (OutstandingToken.objects
                      .filter(blacklistedtoken__isnull=True)
                      .exclude(token=new))
        BlacklistedToken.objects.bulk_create(
            [BlacklistedToken(token=token) for token in old_tokens]
        )


class GameCreateSerializer(serializers.Serializer):
    BROADCAST_TYPE_CHOICES = [
        ("none", "No stream"),
        ("cam", "Camera"),
        ("desktop", "Desktop"),
        ("both", "Camera and desktop"),
    ]
    preferred_color = serializers.ChoiceField(choices=(('white', 'Белый'), ('black', 'Черный')))
    time_control_type = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    broadcast_type = serializers.ChoiceField(choices=BROADCAST_TYPE_CHOICES, default='none')


class GameJoinSerializer(serializers.Serializer):
    preferred_color = serializers.ChoiceField(choices=(('white', 'Белый'), ('black', 'Черный')))


class GameMoveSerializer(serializers.Serializer):
    from_square = serializers.CharField()
    to_square = serializers.CharField()


class GamePgnSerializer(serializers.Serializer):
    results = serializers.CharField()


class TokenCreateSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    name = serializers.CharField()
    active = serializers.BooleanField()
    user_id = serializers.IntegerField()
    expires_in = serializers.IntegerField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

    class Meta:
        ref_name = 'token_refresh'
