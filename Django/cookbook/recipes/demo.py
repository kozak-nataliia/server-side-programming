"""
Run:
  python3 -m recipes.demo
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cookbook.settings")
django.setup()

from recipes.repositories import RepositoryHub 


def reset_demo():
    from recipes.models import (
        RecipeItem, Recipe, Ingredient, Unit, IngredientCategory, RecipeCategory
    )
    RecipeItem.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    Unit.objects.all().delete()
    IngredientCategory.objects.all().delete()
    RecipeCategory.objects.all().delete()


def by_id(repo, pk):
    """Search by ID (works whether repo has get_by_id or not)."""
    if hasattr(repo, "get_by_id"):
        return repo.get_by_id(pk)
    return repo.get(id=pk)


def main():
    repo = RepositoryHub()  # single entry point to all entities & methods

    # -------------------------------
    # WRITE ONE (add) and SHOW result
    # -------------------------------
    breakfast = repo.recipe_categories.get_or_create(name="Breakfast")
    dairy = repo.ingredient_categories.get_or_create(name="Dairy")
    veg = repo.ingredient_categories.get_or_create(name="Vegetable")

    gram = repo.units.get_or_create(name="gram", defaults={"symbol": "g"})
    piece = repo.units.get_or_create(name="piece", defaults={"symbol": "pc"})

    egg = repo.ingredients.get_or_create(name="Egg", defaults={"category": dairy})
    tomato = repo.ingredients.get_or_create(name="Tomato", defaults={"category": veg})
    milk = repo.ingredients.get_or_create(name="Milk", defaults={"category": dairy})

    omelette = repo.recipes.get_or_create(
        title="Simple Omelette",
        defaults={"category": breakfast, "instructions": "Beat eggs, fry, fold. Salt to taste."},
    )
    print(f"[ADD] Category: {breakfast.id} {breakfast}")
    print(f"[ADD] Ingredient: {egg.id} {egg}")
    print(f"[ADD] Recipe: {omelette.id} {omelette}")

    # ensure items exist (idempotent)
    if not repo.items.list(filters={"recipe": omelette}).exists():
        repo.items.add_item(recipe=omelette, ingredient=egg, quantity=3, unit=piece)
        repo.items.add_item(recipe=omelette, ingredient=tomato, quantity=50, unit=gram)
        repo.items.add_item(recipe=omelette, ingredient=milk, quantity=30, unit=gram)
        print("[ADD] 3 items added for recipe")

    # -------------------------------
    # READ (all) and PRINT to screen
    # (demonstrate at least 3 entities)
    # -------------------------------
    print("\n[READ] All Recipe Categories:")
    for c in repo.recipe_categories.list(order_by=["name"]):
        print(f" - {c.id}: {c.name}")

    print("\n[READ] All Ingredients:")
    for ing in repo.ingredients.list(select_related=("category",), order_by=["name"]):
        cat = ing.category.name if ing.category_id else "—"
        print(f" - {ing.id}: {ing.name} (cat: {cat})")

    print("\n[READ] All Recipes:")
    for r in repo.recipes.list(order_by=["title"]):
        print(f" - {r.id}: {r.title}")

    # -------------------------------
    # SEARCH BY ID and PRINT
    # -------------------------------
    found = by_id(repo.recipes, omelette.id)
    print(f"\n[SEARCH BY ID] Recipe {found.id}: {found.title}")

    print("\n[READ] Items for the found recipe:")
    for it in repo.items.items_for(found):
        unit = f"{it.unit}" if it.unit else ""
        print(f" - {it.quantity} {unit} {it.ingredient.name}".strip())


if __name__ == "__main__":
    reset_demo()
    main()
