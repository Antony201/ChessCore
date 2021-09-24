from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.tournament.serializers import tournament
from core.tournament.filters import TournamentFilters
from core.tournament.models import (
    Tournament,
    TournamentType,
)


class TournamentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
        Список турниров

        Список всех турниров
    retrieve:
        Детальные данные турнира

        Детальная страница турнира
    result_table:
        Таблица результатов

        Таблица результатов турнира
    update:
        Редактирование турнира

        Редактирование данных турнира
    partial_update:
        Частичное редактирование турнира

        Частичное редактирование данных турнира
    destroy:
        Удаление турнира

        Удаление данных турнира
    create:
        Создание турнира

        Детальные данные турнира
    """

    class CanActionTournamentPermission(BasePermission):
        """
        Права на доступ
        """

        @staticmethod
        def is_admin(user) -> bool:
            """
            Проверить пользователя что он админ
            """
            if user:
                return any([user.is_staff, user.is_superuser])
            return False

        def has_permission(self, request, view):
            return self.is_admin(request.user)

        def has_object_permission(self, request, view, obj):
            return self.is_admin(request.user)

    queryset = (
        Tournament.objects.select_related("tournament_type")
        .prefetch_related("tours")
        .all()
    )
    serializer_class = tournament.TournamentListSerializer
    filterset_class = TournamentFilters
    permission_classes = []
    tags = ["Tournament"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return tournament.TournamentDetailSerializer

        elif self.action == "create":
            return tournament.TournamentCreateSerializer

        else:
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["destroy", "create", "update", "partial_update"]:
            return [self.CanActionTournamentPermission()]
        return super().get_permissions()

    @swagger_auto_schema(
        method="get",
        responses={200: tournament.TournamentResultTableSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def result_table(self, request, *args, **kwargs):
        qs = self.get_object()
        tour_result = []

        for tour in qs.tours.all():
            tour_result.append(
                {"tour_id": tour.id, "result": tour.get_players_points()}
            )

        serializer = tournament.TournamentResultTableSerializer(
            data=tour_result, many=True
        )

        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class TournamentTypeViewSet(viewsets.ModelViewSet):
    queryset = TournamentType.objects.all()
    serializer_class = tournament.TournamentTypeSerializer
    http_method_names = ["get"]
