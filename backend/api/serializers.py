from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from accounts.models import Follow
from api.serializers_fields import AmountField, Base64ImageField
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite

User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
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
        user_me = self.context['request'].user
        return user_me.follower.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )
        extra_kwargs = {'id': {'read_only': False}}

    # def validate_id(self, value):
    #     if not Ingredient.objects.filter(pk=value).exists():
    #         raise serializers.ValidationError(
    #             'Такого ингредиента нет!'
    #         )
    #     return value


class RecipeIngredientViewSerializer(serializers.ModelSerializer):
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
    tag = TagSerializer(many=True, read_only=True)
    author = UsersSerializer()
    ingredient = RecipeIngredientViewSerializer(many=True)

    # is_favorited = serializers.SerializerMethodField(default=True)
    # is_in_shopping_cart = serializers.SerializerMethodField(default=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tag',
            'author',
            'ingredient',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientCreateSerializer(
        many=True
    )
    tag = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all()),
        allow_empty=False,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
        )

    def recipe_create_or_update(self, instance, validated_data):
        ingredients, tags = (
            validated_data.pop('ingredient'), validated_data.pop('tag')
        )
        for item in ingredients:
            cur_obj, _ = RecipeIngredient.objects.get_or_create(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, pk=item['id']),
                amount=item['amount']
            )
        for item in tags:
            instance.tag.add(item)
        return instance

    def create(self, validated_data):
        raw_data = {
            'ingredient': validated_data.pop('ingredient'),
            'tag': validated_data.pop('tag')
        }
        recipe = Recipe.objects.create(**validated_data)
        return self.recipe_create_or_update(recipe, raw_data)

    def update(self, instance, validated_data):
        instance.ingredient.clear()
        instance.tag.clear()
        instance = self.recipe_create_or_update(instance, validated_data)
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UsersSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSerializer(
        source='recipe_author',
        many=True,
    )

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

    def get_recipes_count(self, obj):
        return obj.recipe_author.count()


class FollowPostSerializer(serializers.ModelSerializer):
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



