from django.core.validators import RegexValidator


class HEXColorValidator(RegexValidator):
    """Валидация username"""
    regex = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    message = 'Введите цвет в HEX формате!'
    flags = 0
