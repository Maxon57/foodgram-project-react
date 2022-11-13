import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class AmountField(serializers.RelatedField):
    """
    Настройка реляционного поля для amount.
    """
    def to_representation(self, value):
        return value.first().amount

    def to_internal_value(self, data):
        return data


class Base64ImageField(serializers.ImageField):
    """
    Создание кастомного поля для сериализации картинки.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
