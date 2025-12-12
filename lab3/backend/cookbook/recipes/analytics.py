from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth

from .models import FavoriteRecipe, Ingredient, Recipe, RecipeComment, RecipeItem, Unit


@dataclass(frozen=True)
class AnalyticsFilters:
    """Filters shared between analytics queries."""

    recipe_category_id: Optional[int] = None
    months: int = 12

    def recipe_q(self) -> Q:
        if self.recipe_category_id:
            return Q(category_id=self.recipe_category_id)
        return Q()


class AnalyticsRepository:
    """6 aggregated ORM queries for the lab.

    Each method returns a QuerySet of dict-like rows (via .values / .values_list).
    The API layer converts them to pandas DataFrames.
    """

    # 1) Top recipes by favorites (group by recipe, join favorites)
    def top_recipes_by_favorites(self, *, limit: int = 10, filters: AnalyticsFilters | None = None):
        filters = filters or AnalyticsFilters()
        return (
            Recipe.objects.filter(filters.recipe_q())
            .annotate(
                favorites_count=Count("favorites", distinct=True),
            )
            .filter(favorites_count__gt=0)  # HAVING favorites_count > 0
            .values(
                "id",
                "title",
                "favorites_count",
                category_name=F("category__name")                
            )
            .order_by("-favorites_count", "title")[:limit]
        )

    # 2) Recipe ratings: avg rating + comments count (group by recipe, join comments)
    def recipe_ratings(self, *, min_comments: int = 1, min_avg_rating: float = 0.0, filters: AnalyticsFilters | None = None):
        filters = filters or AnalyticsFilters()
        return (
            Recipe.objects.filter(filters.recipe_q())
            .annotate(
                comments_count=Count("comments", distinct=True),
                avg_rating=Avg("comments__rating"),
            )
            .filter(comments_count__gte=min_comments)  # HAVING
            .filter(avg_rating__gte=min_avg_rating)
            .values(
                "id",
                "title",
                "comments_count",
                "avg_rating",
                category_name=F("category__name")                
            )
            .order_by("-avg_rating", "-comments_count", "title")
        )

    # 3) Ingredient usage frequency: ingredient + ingredient category, in how many recipes it appears
    def ingredient_usage(self, *, min_recipes: int = 1):
        return (
            Ingredient.objects.annotate(
                recipes_count=Count("used_in__recipe", distinct=True),
                total_items=Count("used_in", distinct=True),
            )
            .filter(recipes_count__gte=min_recipes)  # HAVING
            .values(
                "id",
                "name",
                "recipes_count",
                "total_items",
                category_name=F("category__name")                
            )
            .order_by("-recipes_count", "-total_items", "name")
        )

    # 4) Recipes by ingredient count (+ total quantity): group by recipe, join recipe items
    def recipes_by_ingredient_count(self, *, min_items: int = 1, filters: AnalyticsFilters | None = None):
        filters = filters or AnalyticsFilters()
        return (
            Recipe.objects.filter(filters.recipe_q())
            .annotate(
                ingredients_count=Count("items__ingredient", distinct=True),
                total_quantity=Coalesce(Sum("items__quantity"), 0),
            )
            .filter(ingredients_count__gte=min_items)  # HAVING
            .values(
                "id",
                "title",
                "ingredients_count",
                "total_quantity",
                category_name=F("category__name")                
            )
            .order_by("-ingredients_count", "title")
        )

    # 5) Comments by month: trend + avg rating
    def comments_by_month(self, *, months: int = 12, filters: AnalyticsFilters | None = None):
        filters = filters or AnalyticsFilters(months=months)
        # NOTE: for simplicity we keep all rows; the API can slice by months if needed.
        return (
            RecipeComment.objects.filter(recipe__in=Recipe.objects.filter(filters.recipe_q()))
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                comments_count=Count("id"),
                avg_rating=Avg("rating"),
            )
            .order_by("month")
        )

    # 6) Unit usage: how often units are used in recipe items + average quantity per unit
    def unit_usage(self, *, min_items: int = 1):
        return (
            Unit.objects.annotate(
                items_count=Count("recipeitem", distinct=True),
                avg_quantity=Avg("recipeitem__quantity"),
            )
            .filter(items_count__gte=min_items)  # HAVING
            .values(
                "id",
                "name",
                "symbol",
                "items_count",
                "avg_quantity",
            )
            .order_by("-items_count", "name")
        )
