from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    Purchase,
    Favorite, RecipeIngredient
)


class IngredientInlineAdmin(admin.StackedInline):
    model = RecipeIngredient
    extra = 2
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author'
    ]
    list_filter = (
        'author__username',
        'name',
        'tag__name'
    )
    inlines = [IngredientInlineAdmin]


class IngredientAdmin(admin.ModelAdmin):
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
