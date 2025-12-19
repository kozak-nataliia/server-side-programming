from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

from recipes.models import RecipeCategory
from recipes.repos import BaseRepository

T = TypeVar("T", bound=Model)

class RecipeCategoryRepo(BaseRepository[RecipeCategory]):
    def __init__(self) -> None:
        super().__init__(RecipeCategory)
