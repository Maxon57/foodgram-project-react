from django.db import IntegrityError
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from rest_framework import mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django.db.models import Count
from django.shortcuts import get_object_or_404
from accounts.models import Follow
from recipes.models import Tag, Ingredient, Recipe
from .serializers import UsersSerializer, TagSerializer, \
    RecipeViewSerializer, RecipeCreateSerializer, IngredientSerializer, FollowSerializer, FollowPostSerializer

User = get_user_model()


class UsersViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(
                pk__in=
                [item.author.pk for item in self.request.user.follower.all()]
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
        if self.action == 'retrieve':
            self.permission_classes = [permissions.IsAuthenticated]
        # if self.action in ('list', 'create'):
        #     self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    @action(['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            )
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
    def subscriptions(self, request):
        serializer = self.get_serializer(self.get_queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        data = {
            'user': request.user.pk,
            'author': self.get_object().pk
        }
        if request.method == 'DELETE':
            pass
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = FollowSerializer(
            data=serializer.data,
            context={'request': self.request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeViewSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.perform_create(serializer)
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
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self):
        pass

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self):
        pass

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self):
        pass
