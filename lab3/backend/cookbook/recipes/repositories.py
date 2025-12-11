from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

T = TypeVar("T", bound=Model)


class BaseRepository(Generic[T]):
    """
    wrapper over Django ORM.

    Only:
      - get (single object)
      - create
      - update
      - delete
      - exists
    """

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    # --- basic CRUD / exists ---

    def get(self, **filters) -> T:
        return self.model.objects.get(**filters)

    @transaction.atomic
    def create(self, **data) -> T:
        return self.model.objects.create(**data)

    @transaction.atomic
    def update(self, obj: T, **data) -> T:
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save()
        return obj

    @transaction.atomic
    def delete(self, obj: T) -> None:
        obj.delete()

    def exists(self, **filters) -> bool:
        return self.model.objects.filter(**filters).exists()

from .models import (
    IngredientCategory,
    RecipeCategory,
    Unit,
    Ingredient,
    Recipe,
    RecipeItem,
    RecipeComment, 
    FavoriteRecipe, 
)


class IngredientCategoryRepo(BaseRepository[IngredientCategory]):
    def __init__(self) -> None:
        super().__init__(IngredientCategory)


class RecipeCategoryRepo(BaseRepository[RecipeCategory]):
    def __init__(self) -> None:
        super().__init__(RecipeCategory)


class UnitRepo(BaseRepository[Unit]):
    def __init__(self) -> None:
        super().__init__(Unit)


class IngredientRepo(BaseRepository[Ingredient]):
    def __init__(self) -> None:
        super().__init__(Ingredient)


class RecipeRepo(BaseRepository[Recipe]):
    def __init__(self) -> None:
        super().__init__(Recipe)


class RecipeItemRepo(BaseRepository[RecipeItem]):
    def __init__(self) -> None:
        super().__init__(RecipeItem)

class RecipeCommentRepo(BaseRepository[RecipeComment]):
    def __init__(self) -> None:
        super().__init__(RecipeComment)


class FavoriteRecipeRepo(BaseRepository[FavoriteRecipe]):
    def __init__(self) -> None:
        super().__init__(FavoriteRecipe)


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
