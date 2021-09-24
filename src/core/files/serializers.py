from django.contrib.sites.models import Site
from rest_framework import serializers


from core.files.models.Image import Image


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image50 = serializers.SerializerMethodField()
    image200 = serializers.SerializerMethodField()
    image1000 = serializers.SerializerMethodField()
    image2000 = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ("image", "image50", "image200", "image1000", "image2000")

    def get_image(self, obj):
        return self.build_absolute_url(obj.image.url)

    def get_image50(self, obj):
        return self.build_absolute_url(obj.image.url)

    def get_image200(self, obj):
        return self.build_absolute_url(obj.image.url)

    def get_image1000(self, obj):
        return self.build_absolute_url(obj.image.url)

    def get_image2000(self, obj):
        return self.build_absolute_url(obj.image.url)

    def build_absolute_url(self, path):
        """
        Получение пути к файлу

        Получение пути к файлу в случае если нету объекта request
        Например в веб сокетах.
        """
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(path)
        domain = Site.objects.get_current().domain
        return f'https://{domain}{path}'
