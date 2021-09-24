from rest_framework import serializers

from core.tournament.models import Tour
from core.tournament.serializers.match import MatchSerializer


class TourSerializer(serializers.ModelSerializer):
    matches = MatchSerializer(many=True)

    class Meta:
        model = Tour
        fields = ("id", "start_at", "finished", "matches")


class WriteOnlyTourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        exclude = (
            "created_at",
            "updated_at",
            "deleted_at",
        )
        extra_kwargs = {"start_at": {"required": True}, "finished": {"required": True}}
