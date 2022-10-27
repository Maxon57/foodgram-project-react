from django.contrib.auth import get_user_model
from django.db import models
from django.core import validators

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=150, unique=True)
    color = models.CharField('Цвет', max_length=150, unique=True)
    slug = models.SlugField('Слаг', max_length=50, unique=True)


class Ingredient(models.Model):
    name = models.CharField('Название продукта', max_length=150)
    measurement_unit = models.CharField('Единицы измерения', max_length=10)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            validators.MinValueValidator(1, 'Введите значение больше 0')
        ]
    )


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipe_author'
                               )
    tag = models.ForeignKey(Tag,
                            on_delete=models.SET_NULL,
                            related_name='rec_tag',
                            blank=True,
                            null=True,
                            verbose_name='Тег'
                            )
    ingredient = models.ManyToManyField(Ingredient,
                                        through='RecipeIngredient',
                                        related_name='rec_ingredient'
                                        )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipe/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            validators.MinValueValidator(1, 'Введите значение больше 1')
        ]
    )
    favorite = models.ManyToManyField(User,
                                      through='FavoriteRecipe',
                                      related_name='favorite_rec'
                                      )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.SET_NULL,
                               related_name='recipe',
                               blank=True,
                               null=True)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.SET_NULL,
                                   related_name='ingredient',
                                   blank=True,
                                   null=True)


class FavoriteRecipe(models.Model):
    """Избранное пользователя"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe'
                               )


class Purchases(FavoriteRecipe):
    """Список покупок пользователя"""
    pass
