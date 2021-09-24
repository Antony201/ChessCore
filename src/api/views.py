from django.utils.timezone import datetime
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import re
from django.conf import settings

from . import services
from .models import Elo, Game
from .permissions import GamePermission
from .serializers import CustomTokenObtainPairSerializer, EloSerializer, GameSerializer, GameCreateSerializer, \
    GameJoinSerializer, GameMoveSerializer, GamePgnSerializer, TokenCreateSerializer, TokenRefreshSerializer

from .services import get_pgn_game_from_uuid, repeat_game

User = get_user_model()


class GameViewSet(viewsets.ModelViewSet):
    """
    list:
        Список игр

        Список всех игр
    create:
        Создать игру

        Создать игру и выбрать цвет.
    retrieve:
        Детальныя данные игры

        Детальная страница игры
    delete:
        Удаление игры

        Удалить игру
    partial_update:
        Частичное обновление данных партии

        Частичное обновление данных партии
    update:
        Обновление данных партии

        Обновление детальных данных партии
    move:
        Сделать шаг фигурой в партии

        Сделать шаг в партии одним из участников.
    join:
        Подключиться к игре

        Подключиться как участник игры.
    capitulate:
        Объявить о поражении

        Сдаться одним из участников игры.
    get_unfinished_games:
        Список не завершенных игр

        Список не завершенных игр пользователя
    pgn:
        Отображение PGN доски

        Отображение истории доски в формате PGN
    claim_draw:
        Предложение ничьи

        Предложение одним из игроков ничьи
    agree_draw:
        Согласиться на ничью

        Согласиться на ничью
    repeat_game:
        Повторно создать игру

        Повторно создать игру
    """
    serializer_class = GameSerializer
    queryset = Game.objects.all().order_by("-created_at")

    permission_classes = [GamePermission]

    def _validate_email(self, email):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if re.search(regex, email):
            return True
        else:
            return False

    @swagger_auto_schema(request_body=GameCreateSerializer, responses={201: GameSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(method='put', request_body=GameMoveSerializer, responses={200: GameSerializer})
    @action(detail=True, methods=["put"])
    def move(self, request, *args, **kwargs):
        from_square = request.data.get("from_square")
        to_square = request.data.get("to_square")
        self.user = User.objects.filter(username=request.user).first()
        game_uuid = kwargs.get("pk")
        game = get_object_or_404(Game, uuid=game_uuid)
        board = game.board
        self.check_object_permissions(self.request, game)
        move = services.move_piece(board, from_square, to_square, self.user)

        if move:
            return Response(self.serializer_class(game).data)

        else:
            return Response(
                data={"detail": f"{from_square}{to_square} is not a valid move."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(method='put', request_body=GameJoinSerializer, responses={200: GameSerializer})
    @action(detail=True, methods=["put"])
    def join(self, request, *args, **kwargs):
        game_uuid = kwargs.get("pk")
        preferred_color = request.data.get("preferred_color")

        game = get_object_or_404(Game, uuid=game_uuid)

        services.assign_color(game, request.user, preferred_color=preferred_color)

        serialized_game = GameSerializer(game, context=self.get_serializer_context()).data

        return Response(data=serialized_game)

    @swagger_auto_schema(method="post", request_body=no_body)
    @action(detail=True, methods=["post"])
    def capitulate(self, request, *args, **kwargs):
        game = get_object_or_404(Game, uuid=kwargs.get("pk"))

        self.check_object_permissions(self.request, game)

        services.capitulate_game(game, capitulated_user=request.user)

        return Response(self.serializer_class(game).data)

    @action(detail=False, methods=["get"])
    def get_unfinished_games(self, request, *args, **kwargs):
        user = self.request.user
        games = Game.objects.filter(
            Q(white_player=user) | Q(black_player=user)
        ).order_by("-created_at")

        page = self.paginate_queryset(games)
        serialized_games = self.get_serializer(page, many=True).data

        return (
            self.get_paginated_response(serialized_games)
            if page
            else Response(data=serialized_games)
        )

    @swagger_auto_schema(method="get", responses={200: GamePgnSerializer})
    @action(detail=True, methods=["get"])
    def pgn(self, request, *args, **kwargs):
        game = self.get_object()
        return Response(data={'results': str(get_pgn_game_from_uuid(game.uuid))})

    @swagger_auto_schema(method="post", request_body=no_body)
    @action(detail=True, methods=["post"])
    def claim_draw(self, request, *args, **kwargs):
        game = get_object_or_404(Game, uuid=kwargs.get("pk"))

        self.check_object_permissions(self.request, game)

        claim = services.claim_draw(game, claim_user=request.user)
        if not claim:
            return Response(
                data={"detail": f"You can not claim a draw"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.serializer_class(game).data)

    @swagger_auto_schema(method="post", request_body=no_body)
    @action(detail=True, methods=["post"])
    def agree_draw(self, request, *args, **kwargs):
        game = get_object_or_404(Game, uuid=kwargs.get("pk"))

        self.check_object_permissions(self.request, game)

        claim = services.agree_to_draw(game, agree_user=request.user)
        if not claim:
            return Response(
                data={"detail": f"You can not agree"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self.serializer_class(game).data)

    @swagger_auto_schema(method="post")
    @action(detail=True, methods=["post"])
    def invite(self, request, *args, **kwargs):
        if not request.data['email'] or not self._validate_email(request.data['email']):
            return Response({"detail": "Please insert proper email address."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        game = Game.objects.get(pk=kwargs.get('pk'))

        if game.started_at is None or game.started_at.replace(tzinfo=None) > datetime.now():
            if user in (game.white_player, game.black_player):
                topic = f'Chess game invitation from {user}'
                message = f'''
                    Hello!
                    You have been invited to a chess game:
                    https://chessmatch.mercury.xamtal.ru/#/play/friend/{kwargs.get("pk")}
                '''
                send_mail(
                    topic,
                    message,
                    settings.EMAIL_HOST_USER,
                    [request.data['email']],
                    fail_silently=True,
                )
                return Response({"detail": "An invitation has been successfully sent."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Only participants may send invitations."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "The game has already started"}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(method="get")
    @action(detail=True, methods=["get"])
    def white_player_time(self, request, *args, **kwargs):
        game = Game.objects.filter(uuid=kwargs['pk']).first()
        return Response(data={'results': game.white_player_time(game)})

    @swagger_auto_schema(method="get")
    @action(detail=True, methods=["get"])
    def black_player_time(self, request, *args, **kwargs):
        game = Game.objects.filter(uuid=kwargs['pk']).first()
        return Response(data={'results': game.black_player_time(game)})

    @swagger_auto_schema(method="post", request_body=no_body, responses={201: GameSerializer})
    @action(detail=True, methods=["post"])
    def repeat_game(self, request, *args, **kwargs):
        game = self.get_object()
        new_game = repeat_game(game)
        return Response(self.serializer_class(new_game).data)


class EloViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    list:
        Список Elo

        Список всех Elo
    retrieve:
        Детальные данные Elo

        Детальная страница Elo
    """
    queryset = Elo.objects.all()
    serializer_class = EloSerializer
    lookup_field = "uuid"


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    post:
        Создание токена авторизации

        Создание токена авторизации(access token)
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(responses={200: TokenCreateSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    post:
        Обновление токена авторизации

        Обновление токена авторизации(refresh token)
    """

    @swagger_auto_schema(responses={200: TokenRefreshSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
