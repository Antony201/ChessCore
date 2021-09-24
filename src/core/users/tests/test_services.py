from datetime import datetime, timedelta

import pytest
import jwt
from django.conf import settings
from django.core import mail

from core.users.models import User
from core.users.services import (
    create_user,
    activate_user,
    send_confirm_url_to_email,
    check_confirm_token,
    parse_token
)


@pytest.mark.django_db
def test_create_user():
    user = create_user(
        'test',
        'test',
        'test@test.com',
        'test_first_name',
        'test_last_name'
    )
    expect_user = User.objects.get(username='test')
    assert user == expect_user
    assert user.first_name == expect_user.first_name
    assert user.last_name == expect_user.last_name


@pytest.mark.django_db
def test_activate_user(user):
    user.is_active = False
    user.save()
    assert not User.objects.get(id=user.id).is_active
    activate_user(user.id)
    assert User.objects.get(id=user.id).is_active


@pytest.mark.django_db
def test_confirm_url(user):
    user.email = 'ilgizkasymov@gmail.com'
    user.save()
    send_confirm_url_to_email(user)
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_check_confirm_token(user):
    payload = {'exp': datetime.now() + timedelta(hours=1),
               'user': user.id}
    token = jwt.encode(payload,
                       settings.EMAIL_VERIFICATION_SECRET_KEY,
                       algorithm='HS256').decode("utf-8")
    assert check_confirm_token(token)


@pytest.mark.django_db
def test_parse_token(user):
    payload = {'exp': datetime.now() + timedelta(hours=1),
               'user': user.id}
    token = jwt.encode(payload,
                       settings.EMAIL_VERIFICATION_SECRET_KEY,
                       algorithm='HS256').decode("utf-8")
    assert parse_token(token) == payload
