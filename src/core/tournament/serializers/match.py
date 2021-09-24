from rest_framework import serializers

from core.tournament.models import Match
from core.users.api.serializers import UserSerializer


class MatchSerializer(serializers.ModelSerializer):
    first_player = UserSerializer()
    second_player = UserSerializer()

    class Meta:
        model = Match
        fields = (
            "id",
            "start_at",
            "first_player",
            "second_player",
            "broadcast",
        )


class WriteOnlyMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        )
