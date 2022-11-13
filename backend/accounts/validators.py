from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    """
    Валидация username.
    """
    regex = r'^[\w.@+-]+$'
    message = 'Введите допустимое значение.'
    flags = 0
