from rest_framework import serializers

from core.tournament.models import TimeControlType


class DrawTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeControlType
        fields = (
            "id",
            "name",
        )


class TimeControlTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeControlType
        fields = (
            "id",
            "name",
            "time",
            "additional_time",
        )
