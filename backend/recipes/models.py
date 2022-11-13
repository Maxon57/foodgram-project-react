from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель с тегами к рецептам.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет в HEX формате',
        max_length=150,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        db_table = 'Tag'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель с ингредиентами к рецептам.
    """
    name = models.CharField(
        verbose_name='Название продукта',
        max_length=150,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        db_table = 'Ingredient'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель с рецептами.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe_tag',
        verbose_name='Тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/'
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[
            validators.MinValueValidator
            (
                1, message='Введите значение больше 1'
             )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Время создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        db_table = 'Recipe'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель многие ко многим
    для поля ingredients модели Recipe.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(
                1,
                message='Убедитесь, что это значение больше либо равно 1.'
            )
        ],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        db_table = 'RecipeIngredient'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    """
    Модель для избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        db_table = 'Favorite'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        )

    def __str__(self):
        return f'Избранное: {self.user} - {self.recipe}'


class Purchase(models.Model):
    """
    Модель со списком рецептов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_user',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchase_recipe',
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'Покупка: {self.user} -  {self.recipe}'

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        db_table = 'Purchase'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_purchase',
            ),
        )
