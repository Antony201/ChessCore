from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    ManyToManyField,
    FileField,
    TextField,
    Model,
    BooleanField,
)

from django_paranoid.models import ParanoidModel


User = get_user_model()


class File(Model):
    """ Модель файлов """
    file = FileField()


class Feedback(ParanoidModel):
    title = CharField(max_length=255)
    text = TextField(max_length=2500)
    files = ManyToManyField(File, related_name="files")
    opened = BooleanField(default=True)
    owner = ForeignKey(User, on_delete=CASCADE)

    @property
    def messages_count(self) -> int:
        """ Количество сообщений этого фидбека """
        return Message.objects.filter(feedback_id=self.pk).count()

    @property
    def unread_messages_count(self) -> int:
        """ Количество непрочитанных сообщений """
        return Message.objects.filter(feedback_id=self.pk, readed=False).count()

    def __str__(self):
        return self.title


class Message(ParanoidModel):
    """ Модель сообщений """
    author = ForeignKey(User, on_delete=CASCADE)
    feedback = ForeignKey(Feedback, on_delete=CASCADE, related_name="messages")
    readed = BooleanField(default=False)
    text = TextField(max_length=1200)
    files = ManyToManyField(File, related_name="message_files")
