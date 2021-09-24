from rest_framework import serializers

from core.tournament.models import Tournament, TimeControlType
from core.tournament.serializers.tour import TourSerializer


class TournamentListSerializer(serializers.ModelSerializer):
    tournament_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    draw_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    time_control_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "short_description",
            "description",
            "start_at",
            "tournament_type",
            "tours_amount",
            "members_amount",
            "time_control_type",
            "draw_type",
        )


class TournamentDetailSerializer(serializers.ModelSerializer):
    tournament_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    draw_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    time_control_type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    tours = TourSerializer(many=True)

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "short_description",
            "description",
            "start_at",
            "tournament_type",
            "draw_type",
            "time_control_type",
            "tours_amount",
            "members_amount",
            "tours",
        )


class TournamentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            "name",
            "short_description",
            "description",
            "start_at",
            "tournament_type",
            "draw_type",
            "time_control_type",
        )
        extra_kwargs = {
            "start_at": {"required": True},
            "tournament_type": {"required": True},
            "draw_type": {"required": True},
            "time_control_type": {"required": True},
        }


class TournamentResultTableSerializer(serializers.Serializer):
    class TourResultSerializer(serializers.Serializer):
        username = serializers.CharField()
        point = serializers.FloatField()

    tour_id = serializers.IntegerField()
    result = TourResultSerializer(many=True)


class TournamentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeControlType
        fields = (
            "id",
            "name",
        )
