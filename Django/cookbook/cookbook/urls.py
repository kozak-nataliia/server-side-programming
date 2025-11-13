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
]
