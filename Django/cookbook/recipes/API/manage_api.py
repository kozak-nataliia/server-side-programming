from repositories import RepositoryHub
from managers import (
    RecipeCategoryManager, IngredientCategoryManager,
    UnitManager, IngredientManager, RecipeManager, RecipeItemManager,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

hub = RepositoryHub()
recipe_manager = RecipeManager(hub.recipes)
ingredient_manager = IngredientManager(hub.ingredients)
recipe_item_manager = RecipeItemManager(hub.items)
unit_manager = UnitManager(hub.units)
ingredient_cat_manager = IngredientCategoryManager(hub.ingredient_categories)
recipe_cat_manager = RecipeCategoryManager(hub.recipe_categories)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recipes_summary_view(request):
    """
    Aggregated report for recipes.

    Returns JSON list:
    [
      {
        "recipe_id": 1,
        "title": "Simple Omelette",
        "category": "Breakfast",
        "items_count": 3,
        "total_quantity": 83
      },
      ...
    ]
    """
    data = recipe_item_manager.recipes_summary()
    return Response(data)
