from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.models import Follow
from api.serializers_fields import AmountField, Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Purchase,
    Recipe,
    RecipeIngredient,
    Tag
)

User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    """
    Сериализатор выдачи информации о user.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Проверка на подписку.
        """
        user_me = self.context['request'].user
        if not user_me.is_authenticated:
            return False
        return user_me.follower.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор выдачи информации о тегах.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор выдачи информации о ингредиентах.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецепта, с возможностью
    множественного выбора игредиентов.
    """
    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )
        extra_kwargs = {'id': {'read_only': False}}


class RecipeIngredientViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи рецепта(ов) при GET запросе.
    """
    amount = AmountField(
        source='ingredient_recipe',
        queryset=RecipeIngredient.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи рецепта(ов).
    """
    tags = TagSerializer(many=True)
    author = UsersSerializer()
    ingredients = RecipeIngredientViewSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """
        Проверка рецепта на вхождение в избранное.
        """
        user_me = self.context['request'].user
        if not user_me.is_authenticated:
            return False
        return user_me.favorite_user.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверка рецепта на вхождение в список покупок.
        """
        user_me = self.context['request'].user
        if not user_me.is_authenticated:
            return False
        return user_me.purchase_user.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецепта.
    """
    ingredients = RecipeIngredientCreateSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
        )

    def recipe_create_or_update(self, instance, validated_data):
        """
        Метод для создания или обновления ингредиентов и тегов.
        """
        ingredients, tags = (
            validated_data.pop('ingredients'), validated_data.pop('tags')
        )
        for item in ingredients:
            cur_obj, _ = RecipeIngredient.objects.get_or_create(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, pk=item['id']),
                amount=item['amount']
            )
        for item in tags:
            instance.tags.add(item)

        return instance

    def create(self, validated_data):
        raw_data = {
            'ingredients': validated_data.pop('ingredients'),
            'tags': validated_data.pop('tags')
        }
        recipe = Recipe.objects.create(**validated_data)
        return self.recipe_create_or_update(recipe, raw_data)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.recipe_create_or_update(instance, validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate_ingredients(self, ingredients):
        unique_ingredients = []
        for ingredient in ingredients:
            if ingredient in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиент не может повторяться!'
                )
            unique_ingredients.append(ingredient)
        return ingredients


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи рецепта(ов) с общей информацией.
    """
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UsersSerializer):
    """
    Сериализатор для выдачи подписок.
    """
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, author):
        """
        При наличии в параметрах запроса recipes_limit происходит
        выдача среза списка с ингредиентами.
        """
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            return RecipeSerializer(
                Recipe.objects.filter(author=author)[:int(recipes_limit)],
                context={'queryset': request},
                many=True
            ).data
        return RecipeSerializer(
            Recipe.objects.filter(author=author),
            context={'queryset': request},
            many=True
        ).data

    def get_recipes_count(self, obj):
        """
        Подсчет количества рецептов автора.
        """
        return obj.recipe_author.count()


class FollowPostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создание запроса на подписку.
    """
    class Meta:
        model = Follow
        fields = (
            'author',
            'user'
        )

    def validate(self, data):
        user_me = self.context['request'].user
        if user_me == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        if Follow.objects.filter(
                author=data['author'],
                user=user_me):
            raise serializers.ValidationError(
                f'Вы подписаны на автора {data["author"]}!'
            )
        return data

    def to_representation(self, instance):
        return FollowSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи избранных рецептов.
    """
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        if Favorite.objects.filter(
                user=data['user'],
                recipe=data['recipe']
        ):
            raise serializers.ValidationError(
                f'Рецепт - {data["recipe"]} уже есть в избранном'
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data


class PurchaseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок автора.
    """
    class Meta:
        model = Purchase
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        if Purchase.objects.filter(
                user=data['user'],
                recipe=data['recipe']
        ):
            raise serializers.ValidationError(
                f'Рецепт - {data["recipe"]} уже есть в списке покупок'
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance.recipe).data
