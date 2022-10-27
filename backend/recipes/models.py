from django.contrib.auth import get_user_model
from django.db import models
from django.core import validators

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=150,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX формате',
        max_length=150, unique=True
    )
    slug = models.SlugField(
        'Слаг',
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
    name = models.CharField('Название продукта',
                            max_length=150,
                            db_index=True
                            )
    measurement_unit = models.CharField('Единицы измерения',
                                        max_length=10
                                        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        db_table = 'Ingredient'

    def __str__(self):
        return self.name


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
                                        )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipe/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[
            validators.MinValueValidator(1, 'Введите значение больше 1')
        ]
    )
    pub_date = models.DateTimeField('Время создания',
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
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredient',
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipe',
                                   )
    amount = models.IntegerField(
        default=1,
        validators=[validators.MinValueValidator(1)],
        verbose_name='Количество ингредиента'
    )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    """Избранное пользователя"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_user'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite_recipe'
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
    """Список покупок пользователя"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='purchase_user'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='purchase_recipe'
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
