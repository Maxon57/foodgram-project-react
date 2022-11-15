from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    """
    Фильтрация по ингредиентам.
    """
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """
    Фильтрация рецептов при передаче параметров в запросе.
    """
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def get_is_favorited(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.data.get('is_favorited') == '1':
                return self.queryset.filter(
                    favorite_recipe__user=self.request.user
                )
            else:
                return self.queryset.exclude(
                    favorite_recipe__user=self.request.user
                )
        return self.queryset

    def get_is_in_shopping_cart(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.data.get('is_in_shopping_cart') == '1':
                return self.queryset.filter(
                    purchase_recipe__user=self.request.user
                )
            else:
                return self.queryset.exclude(
                    purchase_recipe__user=self.request.user
                )
        return self.queryset
