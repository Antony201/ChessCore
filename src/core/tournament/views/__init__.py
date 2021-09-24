from rest_framework import viewsets

from core.tournament.models import DrawType, TimeControlType
from core.tournament import serializers


class DrawTypeViewSet(viewsets.ModelViewSet):
    queryset = DrawType.objects.all()
    serializer_class = serializers.DrawTypeSerializer
    http_method_names = ["get"]


class TimeControlTypeViewSet(viewsets.ModelViewSet):
    queryset = TimeControlType.objects.all()
    serializer_class = serializers.TimeControlTypeSerializer
    http_method_names = ["get"]
