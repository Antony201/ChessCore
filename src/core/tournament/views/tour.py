from rest_framework import mixins, viewsets

from core.common import mixins as mixins_
from core.common.permission import AdminOrStaffPermission
from core.tournament.models import Tour
from core.tournament.serializers import tour


class TourViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins_.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list: Список турниров

        Список всех турниров. Требуются права администратора или персонала.
    create: Создание тура

        Создание информации о туре. Требуются права администратора или персонала.
    update: Редактирование тура

        Рудактирование информации о туре. Требуются права администратора или персонала.
    partial_update: Частичное редактирование тура

        Частичное редактирование информации о туре. Требуются права администратора или персонала.
    retrieve: Детальные данные тура

        Детальная страница тура
    destroy: Удаление тура

        Удаление информации о туре. Требуются права администратора или персонала.
    """

    serializer_class = tour.TourSerializer
    queryset = Tour.objects.prefetch_related("matches").all()
    permission_classes = []
    tags = ["Tour"]

    def get_permissions(self):
        if self.action in ("destroy", "create", "update", "partial_update", "list"):
            return [AdminOrStaffPermission()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return tour.WriteOnlyTourSerializer
        else:
            return super().get_serializer_class()
