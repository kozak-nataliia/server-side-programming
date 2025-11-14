"""
Run from the folder with manage.py:
    python -m recipes.demo
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cookbook.settings")
django.setup()

from recipes.repositories import RepositoryHub
from recipes.managers import (
    RecipeCategoryManager,
    IngredientCategoryManager,
    UnitManager,
    IngredientManager,
    RecipeManager,
    RecipeItemManager,
)


def main():
    repo = RepositoryHub()
    repo.delete_all()  # clean for demo

    recipe_cat_manager = RecipeCategoryManager(repo.recipe_categories)
    ingredient_cat_manager = IngredientCategoryManager(repo.ingredient_categories)
    unit_manager = UnitManager(repo.units)
    ingredient_manager = IngredientManager(repo.ingredients)
    recipe_manager = RecipeManager(repo.recipes)
    recipe_item_manager = RecipeItemManager(repo.items)

    # ---------- CREATE ----------
    breakfast = recipe_cat_manager.get_or_create(name="Breakfast")
    dairy = ingredient_cat_manager.get_or_create(name="Dairy")
    veg = ingredient_cat_manager.get_or_create(name="Vegetable")

    gram = unit_manager.get_or_create(name="gram", defaults={"symbol": "g"})
    piece = unit_manager.get_or_create(name="piece", defaults={"symbol": "pc"})

    egg = ingredient_manager.get_or_create(name="Egg", defaults={"category": dairy})
    tomato = ingredient_manager.get_or_create(name="Tomato", defaults={"category": veg})
    milk = ingredient_manager.get_or_create(name="Milk", defaults={"category": dairy})

    omelette = recipe_manager.get_or_create(
        title="Simple Omelette",
        defaults={
            "category": breakfast,
            "instructions": "Beat eggs, fry, fold. Salt to taste.",
        },
    )
    
    cake = recipe_manager.get_or_create(
        title="Cake",
        defaults={
            "category": breakfast,
            "instructions": "Mix everything and bake",
        },
    )
    if not recipe_item_manager.exists(recipe=cake):
        recipe_item_manager.create(
            recipe=cake,
            ingredient=egg,
            quantity=5,
            unit=piece,
        )
        recipe_item_manager.create(
            recipe=cake,
            ingredient=milk,
            quantity=200,
            unit=gram,
        )

    print(f"[ADD] Category: {breakfast.id} {breakfast}")
    print(f"[ADD] Ingredient: {egg.id} {egg}")
    print(f"[ADD] Recipe: {omelette.id} {omelette}")

    if not recipe_item_manager.exists(recipe=omelette):
        recipe_item_manager.create(
            recipe=omelette,
            ingredient=egg,
            quantity=3,
            unit=piece,
        )
        recipe_item_manager.create(
            recipe=omelette,
            ingredient=tomato,
            quantity=50,
            unit=gram,
        )
        recipe_item_manager.create(
            recipe=omelette,
            ingredient=milk,
            quantity=30,
            unit=gram,
        )
        print("[ADD] 3 items added for recipe")

    # ---------- READ & PRINT ----------
    print("\n[READ] All Recipe Categories:")
    for c in recipe_cat_manager.list(order_by=["name"]):
        print(f" - {c.id}: {c.name}")

    print("\n[READ] All Ingredients:")
    for ing in ingredient_manager.list(
        select_related=("category",), order_by=["name"]
    ):
        cat = ing.category.name if ing.category_id else "—"
        print(f" - {ing.id}: {ing.name} (cat: {cat})")

    print("\n[READ] All Recipes:")
    for r in recipe_manager.list(order_by=["title"]):
        print(f" - {r.id}: {r.title}")

    found = recipe_manager.by_id(omelette.id)
    print(f"\n[SEARCH BY ID] Recipe {found.id}: {found.title}")

    print("\n[READ] Items for the found recipe:")
    for it in recipe_item_manager.for_recipe(found):
        unit_str = f"{it.unit}" if it.unit else ""
        print(f" - {it.quantity} {unit_str} {it.ingredient.name}".strip())


if __name__ == "__main__":
    main()
