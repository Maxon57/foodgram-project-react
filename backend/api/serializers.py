from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404
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

    def validate_id(self, value):
        if not Ingredient.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'Такого ингредиента нет!'
            )
        return value


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

    def create(self, validated_data):
        ingredients, tags = (
            validated_data.pop('ingredient'), validated_data.pop('tag')
        )

        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=item['id']),
                amount=item['amount']
            )
        recipe.tag.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        print(instance.__dict__)
        print(updata_or_create)
        return instance