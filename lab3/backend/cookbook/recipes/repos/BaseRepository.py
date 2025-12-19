from __future__ import annotations

from typing import Type, TypeVar, Generic
from django.db import transaction
from django.db import connection
from django.db.models import Model

T = TypeVar("T", bound=Model)

class BaseRepository(Generic[T]):
    """
    wrapper over Django ORM.

    Only:
      - get (single object)
      - create
      - update
      - delete
      - exists
    """

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    # --- basic CRUD / exists ---

    def get(self, **filters) -> T:
        return self.model.objects.get(**filters)

    @transaction.atomic
    def create(self, **data) -> T:
        return self.model.objects.create(**data)

    @transaction.atomic
    def update(self, obj: T, **data) -> T:
        for k, v in data.items():
            setattr(obj, k, v)
        obj.save()
        return obj

    @transaction.atomic
    def delete(self, obj: T) -> None:
        obj.delete()

    def exists(self, **filters) -> bool:
        return self.model.objects.filter(**filters).exists()

