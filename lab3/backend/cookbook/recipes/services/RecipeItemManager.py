from typing import Sequence
from django.db.models import Count, Sum
from recipes.services import RepoManagerBase

class RecipeItemManager(RepoManagerBase):
    def __init__(self, repo):
        super().__init__(repo)

    def for_recipe(self, recipe):
        """
        Convenience method to list items for a given recipe.
        """
        return self.list(
            recipe=recipe,
            select_related=("ingredient", "unit"),
        )
        
    def recipes_summary(self):
        """
        Build a 'ready-to-cook' summary for each recipe.

        Returns a list of dicts:

        [
          {
            "id": 1,
            "title": "Simple Omelette",
            "category": "Breakfast",
            "instructions": "Beat eggs, fry, fold. Salt to taste.",
            "items": [
              {"ingredient": "Egg", "quantity": 3, "unit": "pc"},
              {"ingredient": "Tomato", "quantity": 50, "unit": "g"},
              ...
            ],
            "items_count": 3,
            "total_quantity": 83
          },
          ...
        ]
        """
        # Get all items with related recipe, category, ingredient and unit
        qs = (
            self.repo.model.objects
            .select_related("recipe", "recipe__category", "ingredient", "unit")
            .order_by("recipe__title", "id")
        )

        # We'll accumulate data per recipe_id
        recipes_map: dict[int, dict] = {}

        for item in qs:
            r = item.recipe
            recipe_id = r.id

            # If we haven't seen this recipe yet – create base entry
            if recipe_id not in recipes_map:
                recipes_map[recipe_id] = {
                    "id": recipe_id,
                    "title": r.title,
                    "category": r.category.name if r.category_id else None,
                    "instructions": r.instructions,
                    "items": [],
                    "items_count": 0,
                    "total_quantity": 0,
                }

            entry = recipes_map[recipe_id]

            # Decide what to show for unit; symbol is nicer if present
            unit_obj = item.unit
            if unit_obj is not None:
                unit_str = unit_obj.symbol or unit_obj.name
            else:
                unit_str = None

            # Add ingredient line
            entry["items"].append({
                "ingredient": item.ingredient.name if item.ingredient_id else None,
                "quantity": item.quantity,
                "unit": unit_str,
            })

            # Update counters
            entry["items_count"] += 1
            if item.quantity is not None:
                entry["total_quantity"] += item.quantity

        # Convert map -> list sorted by recipe title
        recipes_list = list(recipes_map.values())
        recipes_list.sort(key=lambda r: r["title"] or "")

        return recipes_list
