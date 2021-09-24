from rest_framework import mixins, viewsets
from rest_framework.permissions import BasePermission

from core.chess.api.serializers import SlideSerializer
from core.chess.models import Slide


class SlideViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    list:
        Список слайдов

        Список всех слайдов
    retrieve:
        Детальные данные слайда

        Детальная страница слайда
    """
    queryset = Slide.objects.filter(published=True).order_by("sorting")
    serializer_class = SlideSerializer
    permission_classes = [BasePermission]

