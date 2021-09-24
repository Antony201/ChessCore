from django.contrib.auth import get_user_model, logout
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status, pagination, filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin
)
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import (
    UserSerializer,
    UserInfoSerializer,
    UserUpdateSerializer,
    AvatarUploadSerializer,
    CreateUserSerializer,
    VerifiedEmailSerializer,
    VerifiedEmailResponseSerializer)

from core.users.services import (
    create_user,
    send_confirm_url_to_email,
    check_confirm_token,
    parse_token,
    activate_user
)

from ...files.models.Image import Image

User = get_user_model()


class UserPagination(pagination.PageNumberPagination):
    page_size = 50


class UserViewSet(RetrieveModelMixin,
                  ListModelMixin,
                  UpdateModelMixin,
                  CreateModelMixin,
                  GenericViewSet):
    """
    list:
        Список пользователей

        Список всех пользователей
    retrieve:
        Детальныя данные пользователя

        Детальная страница пользователя
    partial_update:
        Частичное обновление данных пользователя

        Частичное обновление данных пользователя
    create:
        Создать пользователя

        Создать одного пользователя.
    update:
        Обновление данных пользователя

        Обновление детальных данных пользователя
    confirm_email:
        Подтвердить пользователя

        Подтвердить пользователя с помощью токена
    me:
        Текущий  пользователь

        Текущий авторизованный пользователь
    logout:
        Выйти из системы

        Выйти из системы и скинуть сессию авторизации
    """
    queryset = User.objects.all()
    lookup_field = "username"
    pagination_class = UserPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'update':
            return UserUpdateSerializer

        return UserSerializer

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(is_staff=False, is_superuser=False, is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return []
        return super(UserViewSet, self).get_permissions()

    @action(detail=False, methods=["GET"], description='''
            is_superuser = admin
            is_staff = manager
            is_active = user
            ''')
    def me(self, request):
        base_serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=base_serializer.data)

    @action(detail=False, methods=["GET"])
    def user_info(self, request):
        serializer = UserInfoSerializer(request.user, context={"request": request})

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["PUT"])
    def upload_avatar(self, request, *args, **kwargs):
        serializer = AvatarUploadSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"result":serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        ser = UserUpdateSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({'result': ser.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(method="post")
    def create(self, request, *args, **kwargs):
        ser = CreateUserSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = create_user(**ser.validated_data)
        send_confirm_url_to_email(user)
        return Response({'result': ser.data}, status=status.HTTP_201_CREATED)


    def put(self, request, *args, **kwargs):
        return self.upload_avatar(request, *args, **kwargs)

    @swagger_auto_schema(method="post", request_body=VerifiedEmailSerializer,
                         responses={200: VerifiedEmailResponseSerializer})
    @action(detail=False, methods=["POST"], permission_classes=[])
    def confirm_email(self, request, *args, **kwargs):
        ser = VerifiedEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data['token']
        if check_confirm_token(token):
            data = parse_token(token)
            activate_user(data['user'])
        else:
            raise ValidationError('Invalid token')
        return Response({'result': 'User activated'})

    @swagger_auto_schema(method="get", responses={200: None})
    @action(methods=["GET"], detail=False)
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(method="get")
    @action(methods=["GET"], detail=True)
    def request_reactivation(self, request, *args, **kwargs):
        user = User.objects.filter(username=kwargs['username'])[0]
        send_confirm_url_to_email(user)
        return Response(status=status.HTTP_200_OK)
