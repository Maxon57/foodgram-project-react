from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import UsernameValidator


class User(AbstractUser):
    """
    Кастомная модель User.
    """
    username_validator = UsernameValidator()

    username = models.CharField(
        'username',
        max_length=settings.NAME_LENGTH,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'
        }
    )
    email = models.EmailField(
        "email",
        max_length=settings.EMAIL_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.NAME_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'User'
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель с подписками.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        db_table = 'Follow'
        constraints = (models.UniqueConstraint(
            fields=('user', 'author'),
            name='unique_user_author',
        ),)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
