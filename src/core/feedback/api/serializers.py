from django.contrib.sites.models import Site

from rest_framework import serializers

from core.users.models import User
from core.feedback.models import Feedback, Message, File


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "title",
            "created_at",
            "messages_count",
            "unread_messages_count"
        ]


class FileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "name",
            "url"
        ]

    def get_name(self, obj):
        return obj.file.name

    def get_url(self, obj):
        return self.build_absolute_url(obj.file.url)

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


class MessageAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name")


class MessageSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    author = MessageAuthorSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "author",
            "text",
            "readed",
            "files",
            "created_at",
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    files = FileSerializer(many=True, required=False)

    class Meta:
        model = Message
        fields = [
            "author",
            "feedback",
            "text",
            "files"
        ]

    def save(self):
        text = self.validated_data["text"]
        feedback = self.validated_data["feedback"]
        author = self.validated_data["author"]

        message = Message.objects.create(feedback=feedback, text=text, author=author)

        for file in self.initial_data.getlist("files"):
            file_obj = File.objects.create(file=file)
            message.files.add(file_obj.id)
            message.save()

        return message


class CreateFeedbackSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    files = FileSerializer(many=True, required=False)

    class Meta:
        model = Feedback
        fields = [
            "owner",
            "title",
            "text",
            "files",
        ]

    def save(self):
        title = self.validated_data["title"]
        text = self.validated_data["text"]
        owner = self.validated_data["owner"]

        feedback = Feedback.objects.create(owner=owner, title=title, text=text)

        for file in self.initial_data.getlist("files"):
            file_obj = File.objects.create(file=file)
            feedback.files.add(file_obj.id)
            feedback.save()

        return feedback


class FeedbackDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "created_at",
            "title",
            "text",
            "files",
            "messages",
            "opened"
        ]


class FeedbackCloseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "opened",
        ]

    def update(self, instance, validated_data):
        instance.opened = False
        instance.save()

        return instance
