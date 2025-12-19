from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from django.db.models import Avg, Count, F, Q, Sum, DecimalField, Value
from django.db.models.functions import Coalesce, TruncMonth




@dataclass(frozen=True)

class AnalyticsFilters:
    """Filters shared between analytics queries."""

    recipe_category_id: Optional[int] = None
    months: int = 12

    def recipe_q(self) -> Q:
        if self.recipe_category_id:
            return Q(category_id=self.recipe_category_id)
        return Q()
