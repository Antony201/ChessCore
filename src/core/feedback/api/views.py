from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model


from core.feedback.api.serializers import (
    FeedbackSerializer,
    CreateFeedbackSerializer,
    MessageCreateSerializer,
    FeedbackDetailSerializer,
    FeedbackCloseSerializer
)

from core.feedback.models import Feedback, Message


User = get_user_model()

class FeedbackViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        user = User.objects.get(pk=self.request.user.pk)

        if not (user.is_staff or user.is_superuser):
            self.queryset = self.queryset.filter(owner=user)

        return self.queryset



    def get_serializer_class(self):
        return FeedbackSerializer

    @action(methods=["GET"], detail=True)
    def get_feedback_info(self, request, pk=None):
        feedback = self.get_object()
        messages = Message.objects.filter(feedback=feedback)

        for message in messages:
            message.readed = True
            message.save()

        ser = FeedbackDetailSerializer(feedback)

        return Response({"detail":ser.data}, status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def create_message(self, request):
        serializer = MessageCreateSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"result": serializer.data}, status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def close_feedback(self, request, pk=None):
        feedback = self.get_object()

        if feedback:
            serializer = FeedbackCloseSerializer(feedback, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"result": serializer.data}, status.HTTP_201_CREATED)

        return Response(status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = CreateFeedbackSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
