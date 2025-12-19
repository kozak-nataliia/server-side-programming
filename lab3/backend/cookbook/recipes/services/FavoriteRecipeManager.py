from typing import Sequence
from django.db.models import Count, Sum

from recipes.services import RepoManagerBase

class FavoriteRecipeManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)

    def toggle_favorite(self, user, recipe):
        """
        If favorite exists – delete it and return False.
        If not – create it and return True.
        """
        Model = self.repo.model
        qs = Model.objects.filter(user=user, recipe=recipe)
        if qs.exists():
            qs.delete()
            return False
        self.repo.create(user=user, recipe=recipe)
        return True

    def favorites_for_user(self, user):
        return self.list(
            user=user,
            select_related=("recipe",),
            order_by=["-created_at"],
        )
