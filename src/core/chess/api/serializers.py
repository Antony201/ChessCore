from rest_framework import serializers

from core.chess.models import Slide

from core.files.serializers import ImageSerializer


class SlideSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = Slide
        fields = (
            "name",
            "image",
            "url"
        )
