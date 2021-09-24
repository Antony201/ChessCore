from core.files import serializers as files_serializers
from core.users.models import User
from rest_framework import serializers as serializers
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.validators import UniqueValidator



class UserSerializer(serializers.ModelSerializer):
    avatar = files_serializers.ImageSerializer()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'city',
                  'description',
                  'role',
                  'avatar',
                  'manager',
                  'admin',
                  'user',
                  )

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=256, allow_null=True)

    class Meta:
        model = User
        fields = ["avatar", "username", "email", "first_name", "last_name", "city", "about", "password"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value:
                if attr == 'password':
                    instance.set_password(value)

                else:
                    setattr(instance, attr, value)

        instance.save()

        return instance


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = files_serializers.ImageSerializer()

    class Meta:
        model = User
        fields = ["avatar"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value:
                if attr == 'avatar':
                    ser = files_serializers.ImageSerializer(data=value)
                    ser.is_valid(raise_exception=True)
                    avt = ser.save()

                    instance.avatar = avt

        instance.save()
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
    avatar = files_serializers.ImageSerializer()

    class Meta:
        model = User
        fields = ["avatar", "username", "email", "first_name", "last_name", "city", "about"]


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    confirm_password = serializers.CharField(required=True, max_length=255)

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']
        if password != confirm_password:
            raise ValidationError({
                'confirm_password': 'confirmation password do not match'
            })
        return data

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'city',
            'description',
        )


class VerifiedEmailSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)


class VerifiedEmailResponseSerializer(serializers.Serializer):
    result = serializers.CharField(default='User activated')
