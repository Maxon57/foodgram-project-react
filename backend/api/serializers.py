from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers_fields import AmountField, Base64ImageField
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient

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
        return 'is_subscribed'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
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
            'amount'
        )
        read_only_fields = (
            'name',
            'measurement_unit'
        )


class RecipeViewSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    author = UsersSerializer()
    ingredient = IngredientSerializer(many=True, read_only=True)

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
    ingredient = IngredientSerializer(
        many=True,
        required=True
    )
    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
        )

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredient')
        tags = validated_data.pop('tag')
        # print(ingredients)
        # print(tags)

        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients:
            print(item)
            RecipeIngredient.objects.create(
                recipe=recipe,

            )


        return recipe
