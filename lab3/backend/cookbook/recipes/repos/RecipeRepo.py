from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

from recipes.models import Recipe
from recipes.repos import BaseRepository

T = TypeVar("T", bound=Model)

class RecipeRepo(BaseRepository[Recipe]):
    def __init__(self) -> None:
        super().__init__(Recipe)
