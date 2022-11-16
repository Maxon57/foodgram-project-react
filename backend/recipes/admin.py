from django.contrib import admin

from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredient,
                     Tag)


class IngredientInlineAdmin(admin.StackedInline):
    """
    Редактор админ-панели.
    Добавляет связанные поля из модели Ingredient при создании рецепта.
    """
    model = RecipeIngredient
    extra = 2
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeAdmin(admin.ModelAdmin):
    """
    Настройка админ-панели модели Recipe.
    """
    list_display = [
        'name',
        'author',
        'get_count_favorite'
    ]
    list_filter = (
        'author__username',
        'name',
        'tags__name'
    )
    inlines = [IngredientInlineAdmin]

    def get_count_favorite(self, obj):
        """
        Метод для подсчета количества добавлений в избранное рецепта.
        """
        return obj.favorite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    """
     Настройка админ-панели модели Ingredient.
    """
    list_display = [
        'name',
        'measurement_unit'
    ]
    search_fields = (
        '^name',
    )


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Purchase)
admin.site.register(Favorite)
