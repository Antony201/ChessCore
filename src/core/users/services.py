from datetime import datetime

import jwt
from django.utils.translation import gettext
from jwt.exceptions import (
    InvalidTokenError,
    DecodeError,
    InvalidSignatureError,
    ExpiredSignatureError
)

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import User


def create_user(
    username, password, email, first_name='',
    last_name='', confirm_password=None
) -> User:
    user = User.objects.create_user(username=username,
                                    password=password,
                                    email=email,
                                    first_name=first_name,
                                    last_name=last_name,
                                    is_active=False)
    return user


def activate_user(user_id: int):
    User.objects.filter(id=user_id).update(is_active=True)


def send_confirm_url_to_email(user: User):
    payload = {'exp': datetime.now() + settings.EMAIL_VERIFICATION_EXPIRATION,
               'user': user.id}
    token = jwt.encode(payload,
                       settings.EMAIL_VERIFICATION_SECRET_KEY,
                       algorithm='HS256')
    message = render_to_string('users/email_verification.html', dict(
        url=settings.EMAIL_VERIFICATION_URL,
        token=token
    ))
    plain_message = strip_tags(message)
    mail.send_mail(gettext('Activate your account.'), plain_message,
                   settings.EMAIL_HOST_USER, [user.email],
                   html_message=message)


def check_confirm_token(token: str) -> bool:
    try:
        return bool(jwt.decode(token, settings.EMAIL_VERIFICATION_SECRET_KEY, algorithms=['HS256']))
    except (InvalidTokenError,
            DecodeError,
            InvalidSignatureError,
            ExpiredSignatureError):
        return False


def parse_token(token: str) -> dict:
    return jwt.decode(token, settings.EMAIL_VERIFICATION_SECRET_KEY,
                      algorithms=['HS256'])
