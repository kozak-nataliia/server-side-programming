"""
URL configuration for cookbook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipes.API.viewsets import (
    IngredientViewSet, RecipeViewSet,
    IngredientCategoryViewSet, RecipeCategoryViewSet,
    UnitViewSet, RecipeItemViewSet,
)
from recipes.API.manage_api import (
    recipes_summary_view,
    register_view,
    me_view,
    recipe_comments_view,
    comment_detail_view,
    recipe_toggle_favorite_view,
    my_favorites_view,
)
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredient-categories', IngredientCategoryViewSet, basename='ingredient-category')
router.register(r'recipe-categories', RecipeCategoryViewSet, basename='recipe-category')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'items', RecipeItemViewSet, basename='recipe-item')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/report/recipes-summary/', recipes_summary_view, name='recipes-summary'),
    path("api/token/", obtain_auth_token, name="api_token_auth"),  # POST username + password → токен
    
    # auth
    path("api/auth/register/", register_view, name="register"),
    path("api/auth/me/", me_view, name="me"),
    # comments
    path(
        "api/recipes/<int:recipe_id>/comments/",
        recipe_comments_view,
        name="recipe-comments",
    ),
    path(
        "api/comments/<int:comment_id>/",
        comment_detail_view,
        name="comment-detail",
    ), 
    # favorites
    path(
        "api/recipes/<int:recipe_id>/favorite/",
        recipe_toggle_favorite_view,
        name="recipe-favorite",
    ),
    path("api/me/favorites/", my_favorites_view, name="my-favorites"),
]
