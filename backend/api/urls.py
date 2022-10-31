from django.urls import path, include, re_path
from djoser import views
from rest_framework import routers

from api.views import UsersViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

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
