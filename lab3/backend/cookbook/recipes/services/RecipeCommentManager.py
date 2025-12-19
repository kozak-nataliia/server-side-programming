from typing import Sequence
from django.db.models import Count, Sum
from recipes.services import RepoManagerBase

class RecipeCommentManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)

    def for_recipe(self, recipe):
        return self.list(
            recipe=recipe,
            select_related=("user",),
            order_by=["-created_at"],
        )
