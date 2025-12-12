from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .analytics import AnalyticsFilters, AnalyticsRepository
from .models import RecipeCategory


analytics_repo = AnalyticsRepository()


def _int(request: HttpRequest, key: str, default: int) -> int:
    try:
        return int(request.GET.get(key, default))
    except (TypeError, ValueError):
        return default


def _filters(request: HttpRequest) -> AnalyticsFilters:
    cat = request.GET.get("recipe_category_id")
    try:
        cat_id: Optional[int] = int(cat) if cat not in (None, "") else None
    except (TypeError, ValueError):
        cat_id = None
    return AnalyticsFilters(recipe_category_id=cat_id, months=_int(request, "months", 12))


def _to_div(fig) -> str:
    # CDN is good enough for local dev and for lab screenshots.
    return pio.to_html(fig, include_plotlyjs="cdn", full_html=False)


@login_required
def analytics_dashboard(request: HttpRequest) -> HttpResponse:
    """Plotly dashboard with filters (main part of the lab)."""

    filters = _filters(request)
    limit = _int(request, "limit", 10)
    min_comments = _int(request, "min_comments", 1)
    min_items = _int(request, "min_items", 1)
    min_recipes = _int(request, "min_recipes", 1)

    categories = RecipeCategory.objects.all().order_by("name")

    # 1) favorites
    df_fav = pd.DataFrame(list(analytics_repo.top_recipes_by_favorites(limit=limit, filters=filters)))
    fig_fav = px.bar(
        df_fav,
        x="title" if not df_fav.empty else None,
        y="favorites_count" if not df_fav.empty else None,
        title="Top recipes by favorites",
        hover_data=["category_name"] if (not df_fav.empty and "category_name" in df_fav.columns) else None,
    )

    # 2) ratings
    df_rate = pd.DataFrame(list(analytics_repo.recipe_ratings(min_comments=min_comments, min_avg_rating=0.0, filters=filters)))
    fig_rate = px.scatter(
        df_rate,
        x="comments_count" if not df_rate.empty else None,
        y="avg_rating" if not df_rate.empty else None,
        title="Average rating vs number of comments",
        hover_name="title" if (not df_rate.empty and "title" in df_rate.columns) else None,
    )

    # 3) ingredient usage
    df_ing = pd.DataFrame(list(analytics_repo.ingredient_usage(min_recipes=min_recipes)))
    df_ing_top = df_ing.head(20) if not df_ing.empty else df_ing
    fig_ing = px.bar(
        df_ing_top,
        x="name" if not df_ing_top.empty else None,
        y="recipes_count" if not df_ing_top.empty else None,
        title="Top ingredients by number of recipes",
        hover_data=["category_name", "total_items"] if (not df_ing_top.empty) else None,
    )

    # 4) recipes by ingredient count
    df_items = pd.DataFrame(list(analytics_repo.recipes_by_ingredient_count(min_items=min_items, filters=filters)))
    df_items_top = df_items.head(20) if not df_items.empty else df_items
    fig_items = px.bar(
        df_items_top,
        x="title" if not df_items_top.empty else None,
        y="ingredients_count" if not df_items_top.empty else None,
        title="Recipes by number of ingredients",
        hover_data=["category_name", "total_quantity"] if (not df_items_top.empty) else None,
    )

    # 5) comments trend
    months = _int(request, "months", 12)
    df_trend = pd.DataFrame(list(analytics_repo.comments_by_month(months=months, filters=filters)))
    if not df_trend.empty and "month" in df_trend.columns:
        df_trend["month"] = pd.to_datetime(df_trend["month"])
    fig_trend = px.line(
        df_trend,
        x="month" if not df_trend.empty else None,
        y="comments_count" if not df_trend.empty else None,
        title="Comments per month",
    )

    # 6) units distribution
    df_units = pd.DataFrame(list(analytics_repo.unit_usage(min_items=1)))
    df_units_top = df_units.head(15) if not df_units.empty else df_units
    fig_units = px.pie(
        df_units_top,
        names="symbol" if (not df_units_top.empty and "symbol" in df_units_top.columns) else ("name" if not df_units_top.empty else None),
        values="items_count" if not df_units_top.empty else None,
        title="Unit usage distribution",
    )

    context: Dict[str, Any] = {
        "categories": categories,
        "filters": filters,
        "limit": limit,
        "min_comments": min_comments,
        "min_items": min_items,
        "min_recipes": min_recipes,
        "months": months,
        "plot_favorites": _to_div(fig_fav),
        "plot_ratings": _to_div(fig_rate),
        "plot_ingredients": _to_div(fig_ing),
        "plot_items": _to_div(fig_items),
        "plot_trend": _to_div(fig_trend),
        "plot_units": _to_div(fig_units),
    }

    return render(request, "recipes/dashboard.html", context)
