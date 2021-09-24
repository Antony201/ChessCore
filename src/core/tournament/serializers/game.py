from rest_framework import serializers

from api.models import Game


class WriteOnlyGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("white_player", "black_player",)
        extra_kwargs = {"white_player": {"required": True}, "black_player": {"required": True}}
