from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import filters, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.models import Follow
from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)

from .filters import RecipeFilter
from .permissions import CustomerAccessPermission
from .serializers import (FavoriteSerializer, FollowPostSerializer,
                          FollowSerializer, IngredientSerializer,
                          PurchaseSerializer, RecipeCreateSerializer,
                          RecipeViewSerializer, TagSerializer, UsersSerializer)

User = get_user_model()


class UsersViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        if self.action == 'subscriptions':
            subscriptions = self.request.user.follower.all()
            return User.objects.filter(
                pk__in=[item.author.pk for item in subscriptions]
            )
        return User.objects.order_by('id').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscriptions':
            return FollowSerializer
        if self.action == 'subscribe':
            return FollowPostSerializer
        return UsersSerializer

    def get_permissions(self):
        if self.action in (
                'retrieve',
                'me',
                'set_password',
                'subscribe',
                'subscriptions'
        ):
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        data = {
            'author': self.get_object().pk,
            'user': self.request.user.pk,
        }
        serializer = FollowPostSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk):
        follow = Follow.objects.filter(
            author=self.get_object(),
            user=self.request.user
        )
        if not follow:
            raise ValidationError(
                'Вы не были подписаны на автора'
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action == 'shopping_cart':
            return PurchaseSerializer
        return RecipeViewSerializer

    def get_permissions(self):
        if self.action in (
                'create',
                'download_shopping_cart',
                'shopping_cart',
                'favorite'
        ):
            self.permission_classes = [permissions.IsAuthenticated]
        if self.action in ('partial_update', 'destroy'):
            self.permission_classes = [CustomerAccessPermission]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.save()
        serializer = RecipeViewSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeViewSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            headers=self.get_success_headers(serializer.data)
        )

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs['pk'])

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__purchase_recipe__user=request.user
        ).values(
            name=F('ingredients__name'),
            measurement_unit=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        shopping_list = 'Игредиенты:\n\n'
        shopping_list += '\n'.join([
            f' - {ingredient["name"]}'
            f' - ({ingredient["measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(
            shopping_list,
            content_type='text/plain'
        )
        filename = f'{self.request.user.username}_shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(methods=['POST'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        return self.favorite(request, *args, **kwargs)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        purchase = Purchase.objects.filter(
            user=request.user.pk,
            recipe=self.get_recipe()
        )
        if not purchase:
            raise ValidationError(
                'Рецепта в спске покупок нет!'
            )
        purchase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=True)
    def favorite(self, request, *args, **kwargs):
        data = {
            'user': request.user.pk,
            'recipe': self.get_recipe().pk
        }
        serializer = self.get_serializer(
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        favorite = Favorite.objects.filter(
            user=request.user.pk,
            recipe=self.get_recipe()
        )
        if not favorite:
            raise ValidationError(
                'Рецепта в избранном нет!'
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
