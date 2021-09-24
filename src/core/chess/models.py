from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    IntegerField,
    Model,
)


from core.files.models.Image import Image


class Slide(Model):
    name = CharField(max_length=255)
    url = CharField(max_length=255, blank=True, default="")
    image = ForeignKey(Image, on_delete=CASCADE)
    sorting = IntegerField(unique=True)
    published = BooleanField()

    def __str__(self):
        return self.name
