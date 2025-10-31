from __future__ import annotations
from typing import Iterable, Optional, Type, TypeVar, Generic, Dict, Any, Sequence
from django.db import transaction
from django.db.models import Model, QuerySet

T = TypeVar("T", bound=Model)

class BaseRepository(Generic[T]):
    """Tiny repository wrapper around Django ORM (swappable data source later)."""

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def get(self, **filters) -> T:
        return self.model.objects.get(**filters)

    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Sequence[str]] = None,
        select_related: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> QuerySet[T]:
        qs: QuerySet[T] = self.model.objects.all()
        if filters:
            qs = qs.filter(**filters)
        if select_related:
            qs = qs.select_related(*select_related)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs[:limit] if limit else qs

    @transaction.atomic
    def create(self, **data) -> T:
        return self.model.objects.create(**data)

    @transaction.atomic
    def update(self, obj: T, **data) -> T:
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save(update_fields=list(data.keys()))
        return obj

    @transaction.atomic
    def delete(self, obj: T) -> None:
        obj.delete()

    def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **lookup) -> T:
        obj, _ = self.model.objects.get_or_create(defaults=defaults or {}, **lookup)
        return obj
    
    def get_by_id(self, pk: int) -> T:
        return self.model.objects.get(pk=pk)


# --- Concrete repos (explicit types, easy to import in demo) ---
from .models import IngredientCategory, RecipeCategory, Unit, Ingredient, Recipe, RecipeItem  # noqa: E402


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

    def add_item(self, *, recipe: Recipe, ingredient: Ingredient, quantity, unit: Optional[Unit]):
        return self.create(recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit)

    def items_for(self, recipe: Recipe) -> Iterable[RecipeItem]:
        return self.list(filters={"recipe": recipe}, select_related=("ingredient", "unit"))

class RepositoryHub:
    """
    Single entry point to all entities and their methods.
    """
    def __init__(self) -> None:
        self.ingredient_categories = IngredientCategoryRepo()
        self.recipe_categories = RecipeCategoryRepo()
        self.units = UnitRepo()
        self.ingredients = IngredientRepo()
        self.recipes = RecipeRepo()
        self.items = RecipeItemRepo()
