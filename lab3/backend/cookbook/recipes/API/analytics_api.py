from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from recipes.api.permissions import IsAdminOrReadOnly

from recipes.analytics import AnalyticsFilters, AnalyticsRepository


analytics_repo = AnalyticsRepository()


def _int(q: Dict[str, Any], key: str, default: int) -> int:
    try:
        return int(q.get(key, default))
    except (TypeError, ValueError):
        return default


def _float(q: Dict[str, Any], key: str, default: float) -> float:
    try:
        return float(q.get(key, default))
    except (TypeError, ValueError):
        return default


def _filters(q: Dict[str, Any]) -> AnalyticsFilters:
    category_id = q.get("recipe_category_id")
    try:
        category_id_int: Optional[int] = int(category_id) if category_id not in (None, "") else None
    except (TypeError, ValueError):
        category_id_int = None
    months = _int(q, "months", 12)
    return AnalyticsFilters(recipe_category_id=category_id_int, months=months)


def _df_response(df: pd.DataFrame, *, stats_columns: Optional[list[str]] = None) -> Response:
    # Basic stats for selected numeric columns (mean/median/min/max)
    stats: Dict[str, Any] = {}
    if stats_columns:
        for col in stats_columns:
            if col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce")
                stats[col] = {
                    "mean": None if s.isna().all() else float(s.mean()),
                    "median": None if s.isna().all() else float(s.median()),
                    "min": None if s.isna().all() else float(s.min()),
                    "max": None if s.isna().all() else float(s.max()),
                }

    return Response(
        {
            "rows": df.to_dict(orient="records"),
            "stats": stats,
            "columns": list(df.columns),
        }
    )


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def top_recipes_by_favorites_df(request):
    limit = _int(request.query_params, "limit", 10)
    rows = list(analytics_repo.top_recipes_by_favorites(limit=limit, filters=_filters(request.query_params)))
    df = pd.DataFrame(rows)
    return _df_response(df, stats_columns=["favorites_count"])


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def recipe_ratings_df(request):
    min_comments = _int(request.query_params, "min_comments", 1)
    min_avg = _float(request.query_params, "min_avg_rating", 0.0)
    rows = list(
        analytics_repo.recipe_ratings(
            min_comments=min_comments,
            min_avg_rating=min_avg,
            filters=_filters(request.query_params),
        )
    )
    df = pd.DataFrame(rows)
    return _df_response(df, stats_columns=["comments_count", "avg_rating"])


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def ingredient_usage_df(request):
    min_recipes = _int(request.query_params, "min_recipes", 1)
    rows = list(analytics_repo.ingredient_usage(min_recipes=min_recipes))
    df = pd.DataFrame(rows)
    return _df_response(df, stats_columns=["recipes_count", "total_items"])


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def recipes_by_ingredient_count_df(request):
    min_items = _int(request.query_params, "min_items", 1)
    rows = list(analytics_repo.recipes_by_ingredient_count(min_items=min_items, filters=_filters(request.query_params)))
    df = pd.DataFrame(rows)
    return _df_response(df, stats_columns=["ingredients_count", "total_quantity"])


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def comments_by_month_df(request):
    months = _int(request.query_params, "months", 12)
    rows = list(analytics_repo.comments_by_month(months=months, filters=_filters(request.query_params)))
    df = pd.DataFrame(rows)
    if not df.empty and "month" in df.columns:
        # make ISO strings for JSON
        df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m-01")
    return _df_response(df, stats_columns=["comments_count", "avg_rating"])


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def unit_usage_df(request):
    min_items = _int(request.query_params, "min_items", 1)
    rows = list(analytics_repo.unit_usage(min_items=min_items))
    df = pd.DataFrame(rows)
    return _df_response(df, stats_columns=["items_count", "avg_quantity"])
