from typing import Sequence
from django.db.models import Count, Sum
from recipes.services import RepoManagerBase

class IngredientManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)
