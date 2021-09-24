from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework import status


from . import serializers
from .models.Image import Image


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = Image.objects.all()
    http_method_names = ('post',)

    @action(methods=['post'], detail=True)
    def post(self, request, *args, **kwargs):
        try:
            image = request.FILES['image']
            # Image processing here.
            return Response(status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'Expected image.'})
