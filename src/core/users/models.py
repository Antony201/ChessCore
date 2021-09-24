from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(AbstractUser):
    active = models.BooleanField(default=True)
    avatar = models.ForeignKey('files.Image', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    email = models.EmailField('email address', blank=True, unique=True)
    about = models.CharField(max_length=1200, blank=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def manager(self):
        return self.is_staff

    @property
    def admin(self):
        return self.is_superuser

    @property
    def user(self):
        return not self.is_staff and not self.is_superuser

    def __str__(self):
        return self.username
