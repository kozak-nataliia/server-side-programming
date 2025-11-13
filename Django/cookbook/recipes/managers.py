from typing import Sequence
from django.db.models import Count, Sum

class RepoManagerBase:
    """
    High-level operations on top of a repository.

    - uses repo.get/create/update/delete/exists
    - adds get_or_create, list, filters, etc.
    """

    def __init__(self, repo):
        self.repo = repo  # BaseRepository instance

    # ---- single-object helpers ----

    def get_or_create(self, defaults=None, **lookup):
        if self.repo.exists(**lookup):
            return self.repo.get(**lookup)
        data = {**lookup, **(defaults or {})}
        return self.repo.create(**data)

    def by_id(self, pk):
        return self.repo.get(id=pk)

    def exists(self, **filters):
        return self.repo.exists(**filters)

    def create(self, **data):
        return self.repo.create(**data)

    def update(self, obj, **data):
        return self.repo.update(obj, **data)

    def delete(self, obj):
        return self.repo.delete(obj)

    # ---- QuerySet-based helpers ----

    def list(
        self,
        order_by: Sequence[str] | None = None,
        select_related: Sequence[str] | None = None,
        **filters,
    ):
        """
        Return a QuerySet of model instances.
        """
        qs = self.repo.model.objects  # Django Manager

        if filters:
            qs = qs.filter(**filters)
        else:
            qs = qs.all()

        if select_related:
            qs = qs.select_related(*select_related)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


class RecipeCategoryManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)


class IngredientCategoryManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)


class UnitManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)


class IngredientManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)


class RecipeManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)


class RecipeItemManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)

    def for_recipe(self, recipe):
        """
        Convenience method to list items for a given recipe.
        """
        return self.list(
            recipe=recipe,
            select_related=("ingredient", "unit"),
        )
        
    def recipes_summary(self):
        """
        Return aggregated data per recipe.

        For each recipe:
        - recipe_id
        - title
        - category_name (or None)
        - items_count (how many RecipeItem rows)
        - total_quantity (sum of quantities, may be None)

        Returns a plain Python list of dicts, ready for JSON.
        """
        qs = (
            self.repo.model.objects  # RecipeItem model
            .select_related("recipe", "recipe__category")
            .values("recipe_id", "recipe__title", "recipe__category__name")
            .annotate(
                items_count=Count("id"),
                total_quantity=Sum("quantity"),
            )
            .order_by("recipe__title")
        )

        result = []
        for row in qs:
            result.append({
                "recipe_id": row["recipe_id"],
                "title": row["recipe__title"],
                "category": row["recipe__category__name"],
                "items_count": row["items_count"],
                "total_quantity": row["total_quantity"],
            })
        return result
