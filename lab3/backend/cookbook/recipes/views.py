from __future__ import annotations

from math import pi
from typing import Any, Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .analytics import AnalyticsFilters, AnalyticsRepository
from .models import RecipeCategory

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource
from django.contrib.admin.views.decorators import staff_member_required

from decimal import Decimal

def df_make_json_safe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    # convert Decimal -> float (or str, but float is better for charts)
    return df.applymap(lambda v: float(v) if isinstance(v, Decimal) else v)

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


@staff_member_required
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

@staff_member_required
def analytics_dashboard_v2_bokeh(request: HttpRequest) -> HttpResponse:
    # same filters as plotly dashboard
    category_id = request.GET.get("recipe_category_id") or None
    limit = int(request.GET.get("limit", 10))
    min_comments = int(request.GET.get("min_comments", 1))
    min_items = int(request.GET.get("min_items", 1))
    min_recipes = int(request.GET.get("min_recipes", 1))
    months = int(request.GET.get("months", 12))

    filters = AnalyticsFilters(recipe_category_id=int(category_id) if category_id else None, months=months)

    # DataFrames (same 6 aggregated queries)
    df_fav   = df_make_json_safe(pd.DataFrame(list(analytics_repo.top_recipes_by_favorites(limit=limit, filters=filters))))
    df_rate  = df_make_json_safe(pd.DataFrame(list(analytics_repo.recipe_ratings(min_comments=min_comments, min_avg_rating=0.0, filters=filters))))
    df_ing   = df_make_json_safe(pd.DataFrame(list(analytics_repo.ingredient_usage(min_recipes=min_recipes))))
    df_items = df_make_json_safe(pd.DataFrame(list(analytics_repo.recipes_by_ingredient_count(min_items=min_items, filters=filters))))
    df_trend = df_make_json_safe(pd.DataFrame(list(analytics_repo.comments_by_month(months=months, filters=filters))))
    df_units = df_make_json_safe(pd.DataFrame(list(analytics_repo.unit_usage(min_items=1))))

    # 1) bar: favorites
    p1 = figure(height=280, title="Top recipes by favorites", x_range=list(df_fav["title"]) if not df_fav.empty else [])
    if not df_fav.empty:
        src = ColumnDataSource(df_fav)
        p1.vbar(x="title", top="favorites_count", source=src, width=0.9)
        p1.xaxis.major_label_orientation = 1.1

    # 2) scatter: rating vs comments
    p2 = figure(height=280, title="Avg rating vs comments")
    if not df_rate.empty:
        src = ColumnDataSource(df_rate)
        p2.circle(x="comments_count", y="avg_rating", size=10, source=src)

    # 3) bar: ingredient usage (top 20)
    p3 = figure(height=280, title="Top ingredients by recipes", x_range=list(df_ing.head(20)["name"]) if not df_ing.empty else [])
    if not df_ing.empty:
        top = df_ing.head(20)
        src = ColumnDataSource(top)
        p3.vbar(x="name", top="recipes_count", source=src, width=0.9)
        p3.xaxis.major_label_orientation = 1.1

    # 4) bar: recipes by ingredient count (top 20)
    p4 = figure(height=280, title="Recipes by ingredient count", x_range=list(df_items.head(20)["title"]) if not df_items.empty else [])
    if not df_items.empty:
        top = df_items.head(20)
        src = ColumnDataSource(top)
        p4.vbar(x="title", top="ingredients_count", source=src, width=0.9)
        p4.xaxis.major_label_orientation = 1.1

    # 5) line: comments trend
    p5 = figure(height=280, title="Comments by month", x_axis_type="datetime")
    if not df_trend.empty and "month" in df_trend.columns:
        df_trend["month"] = pd.to_datetime(df_trend["month"])
        src = ColumnDataSource(df_trend)
        p5.line(x="month", y="comments_count", source=src, line_width=3)
        p5.circle(x="month", y="comments_count", source=src, size=7)

    top = df_units.head(3).copy()
    if top.empty:
        # optionally show "no data" text instead of a blank plot
        p6 = figure(height=280, title="Unit usage (top 3)", toolbar_location=None)
    else:
        # IMPORTANT: ensure numeric (avoid Decimal issues)
        top["items_count"] = top["items_count"].astype(float)

        top["angle"] = top["items_count"] / top["items_count"].sum() * 2 * pi
        top["end_angle"] = top["angle"].cumsum()
        top["start_angle"] = top["end_angle"] - top["angle"]
        top["color"] = ["#718dbf", "#e84d60", "#ddb7b1"][:len(top)]

        p6 = figure(
            height=280,
            title="Unit usage (top 3)",
            toolbar_location=None,
            tools="hover",
            tooltips="@name: @items_count",
            x_range=(-2, 2),
            y_range=(-2, 2),
        )

        p6.wedge(
            x=0, y=0,
            radius=0.7,
            start_angle="start_angle",
            end_angle="end_angle",
            line_color="white",
            fill_color="color",
            source=ColumnDataSource(top),
        )

        p6.axis.visible = False
        p6.grid.grid_line_color = None

    scripts_divs = [components(p) for p in [p1, p2, p3, p4, p5, p6]]
    context = {
        "categories": RecipeCategory.objects.all().order_by("name"),
        "filters": filters,
        "limit": limit,
        "min_comments": min_comments,
        "min_items": min_items,
        "min_recipes": min_recipes,
        "months": months,
        "bokeh_resources": CDN.render(),
        "plots": [{"script": s, "div": d} for (s, d) in scripts_divs],
    }
    return render(request, "recipes/dashboard_bokeh.html", context)
