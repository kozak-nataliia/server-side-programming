from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

from recipes.models import RecipeItem
from recipes.repos import BaseRepository

T = TypeVar("T", bound=Model)

class RecipeItemRepo(BaseRepository[RecipeItem]):
    def __init__(self) -> None:
        super().__init__(RecipeItem)
