from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UsersViewSet)
from django.urls import include, path, re_path
from djoser import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')

auth_urlpatterns = [
    re_path(
        r"^token/login/?$",
        views.TokenCreateView.as_view(),
        name="login"
    ),
    re_path(
        r"^token/logout/?$",
        views.TokenDestroyView.as_view(),
        name="logout"
    )
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('', include(router.urls))
]
