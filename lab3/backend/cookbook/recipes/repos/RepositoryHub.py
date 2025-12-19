from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

from recipes.repos import FavoriteRecipeRepo, IngredientCategoryRepo, IngredientRepo, RecipeCategoryRepo, RecipeCommentRepo, RecipeItemRepo, RecipeRepo, UnitRepo

T = TypeVar("T", bound=Model)

class RepositoryHub:
    """
    Single entry point to all repositories.
    """

    def __init__(self) -> None:
        self.ingredient_categories = IngredientCategoryRepo()
        self.recipe_categories = RecipeCategoryRepo()
        self.units = UnitRepo()
        self.ingredients = IngredientRepo()
        self.recipes = RecipeRepo()
        self.items = RecipeItemRepo()
        self.recipe_comments = RecipeCommentRepo()  
        self.favorites = FavoriteRecipeRepo()

    def delete_all(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE
                    recipes_recipeitem,
                    recipes_recipe,
                    recipes_ingredient,
                    recipes_unit,
                    recipes_ingredientcategory,
                    recipes_recipecategory,
                    recipes_recipecomment,
                    recipes_favoriterecipe
                RESTART IDENTITY CASCADE;
            """)
