from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import Game
from api.serializers import GameSerializer
from core.common import mixins as mixins_
from core.common.permission import AdminOrStaffPermission
from core.tournament.models import Match
from core.tournament.serializers import match
from core.tournament.serializers.game import WriteOnlyGameSerializer


class MatchPlayerException(APIException):
    default_code = 'player_not_found'
    default_detail = _('Players are not part of the match')
    status_code = status.HTTP_400_BAD_REQUEST


class MatchGameException(APIException):
    default_code = 'game_not_found'
    default_detail = _('Game is not found')
    status_code = status.HTTP_404_NOT_FOUND


class MatchViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins_.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    create: Создание матча

        Создание информации о матче. Требуются права администратора или персонала.
    update: Редактирование матча

        Редактирование информации о матче. Требуются права администратора или персонала.
    partial_update: Частичное редактирование матча

        Частичное редактирование информации о матче. Требуются права администратора или персонала.
    destroy: Удаление матча

        Удаление информации о матче. Требуются права администратора или персонала.
    games:
        Партии игры

        Все партии одной игры
    """

    serializer_class = match.MatchSerializer
    queryset = Match.objects.all()
    permission_classes = []
    tags = ["Match"]

    def get_permissions(self):
        if self.action in (
            "destroy",
            "create",
            "update",
            "partial_update",
        ):
            return [AdminOrStaffPermission()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return match.WriteOnlyMatchSerializer
        else:
            return super().get_serializer_class()

    @swagger_auto_schema(method="get", responses={200: GameSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def games(self, request: Request, *args, **kwargs) -> Response:
        match_ = self.get_object()
        return Response(GameSerializer(match_.games.all(), many=True).data)


@method_decorator(name='create', decorator=swagger_auto_schema(
    request_body=WriteOnlyGameSerializer, responses={201: GameSerializer()}
))
class MatchGameViewSet(viewsets.GenericViewSet):
    """
    create: Создание игры матча

        Создание информации об игре матча. Требуются права администратора или персонала.
    destroy: Удаление игры матча

        Удаление информации об игре матче. Требуются права администратора или персонала.
    """
    queryset = Match.objects.all()
    permission_classes = [AdminOrStaffPermission]
    tags = ["Match"]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = WriteOnlyGameSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        match_ = self.get_object()
        match_players = (match_.first_player_id, match_.second_player_id)

        for _, value in serializer.data.items():
            if value not in match_players:
                raise MatchPlayerException

        # TODO: Реализовать service для работы с Играми
        game = Game.objects.create(
            broadcast_type=Game.BOTH,
            time_control_type=match_.tournament.time_control_type,
            **serializer.validated_data
        )

        match_.games.add(game)
        match_.save()

        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        match_ = self.get_object()

        # TODO: Реализовать service для работы с Играми
        try:
            game = match_.games.get(uuid=kwargs.get('game'))
        except Game.DoesNotExist:
            raise MatchGameException

        match_.games.remove(game)
        match_.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
