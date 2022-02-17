from datetime import datetime
from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value == 'me':
        raise ValidationError(
            ('Username can`t be "me"'),
            params={'value': value},
        )


def validate_year(value):
    now = datetime.now().year
    if value > now:
        raise ValidationError(
            'Год не может больше текущего')
