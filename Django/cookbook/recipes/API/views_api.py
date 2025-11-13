from repositories import RepositoryHub
from managers import (
    RecipeCategoryManager, IngredientCategoryManager,
    UnitManager, IngredientManager, RecipeManager, RecipeItemManager,
)

hub = RepositoryHub()
recipe_manager = RecipeManager(hub.recipes)
ingredient_manager = IngredientManager(hub.ingredients)
recipe_item_manager = RecipeItemManager(hub.items)
unit_manager = UnitManager(hub.units)
ingredient_cat_manager = IngredientCategoryManager(hub.ingredient_categories)
recipe_cat_anager = RecipeCategoryManager(hub.recipe_categories)
