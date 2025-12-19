"""
Run from the folder with manage.py:
    python -m recipes.demo
"""
from decimal import Decimal
import os
import random
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cookbook.settings")
django.setup()

from recipes.repos import RepositoryHub
from recipes.services import (
    FavoriteRecipeManager,
    RecipeCategoryManager,
    IngredientCategoryManager,
    RecipeCommentManager,
    UnitManager,
    IngredientManager,
    RecipeManager,
    RecipeItemManager,
)

from django.contrib.auth import get_user_model
User = get_user_model()

def main():
    repo = RepositoryHub()
    repo.delete_all()  # clean for demo

# ---------- MANAGERS ----------
    recipe_cat_manager = RecipeCategoryManager(repo.recipe_categories)
    ingredient_cat_manager = IngredientCategoryManager(repo.ingredient_categories)
    unit_manager = UnitManager(repo.units)
    ingredient_manager = IngredientManager(repo.ingredients)
    recipe_manager = RecipeManager(repo.recipes)
    recipe_item_manager = RecipeItemManager(repo.items)
    comment_manager = RecipeCommentManager(repo.recipe_comments)
    favorite_manager = FavoriteRecipeManager(repo.favorites)

    # ---------- USERS (must exist) ----------
    users = list(User.objects.all().order_by("id")[:5])
    if not users:
        raise RuntimeError(
            "No users found. Create at least 1 user first (admin or regular), "
            "then rerun: python -m recipes.demo"
        )

    # ---------- CATEGORIES ----------
    recipe_categories = [
        recipe_cat_manager.get_or_create(name=n)
        for n in ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"]
    ]

    ingredient_categories = [
        ingredient_cat_manager.get_or_create(name=n)
        for n in ["Dairy", "Vegetable", "Fruit", "Meat", "Grain", "Spice"]
    ]

    # ---------- UNITS ----------
    # symbol is UNIQUE, so keep them distinct
    units = [
        unit_manager.get_or_create(name="Gram", defaults={"symbol": "g"}),
        unit_manager.get_or_create(name="Milliliter", defaults={"symbol": "ml"}),
        unit_manager.get_or_create(name="Piece", defaults={"symbol": "pc"}),
    ]

    # ---------- INGREDIENTS ----------
    ingredient_names = [
        ("Milk", "Dairy"),
        ("Cheese", "Dairy"),
        ("Butter", "Dairy"),
        ("Egg", "Dairy"),
        ("Tomato", "Vegetable"),
        ("Potato", "Vegetable"),
        ("Onion", "Vegetable"),
        ("Carrot", "Vegetable"),
        ("Garlic", "Vegetable"),
        ("Apple", "Fruit"),
        ("Banana", "Fruit"),
        ("Chicken breast", "Meat"),
        ("Beef", "Meat"),
        ("Rice", "Grain"),
        ("Pasta", "Grain"),
        ("Flour", "Grain"),
        ("Salt", "Spice"),
        ("Pepper", "Spice"),
        ("Sugar", "Spice"),
        ("Olive oil", "Spice"),
    ]

    ingredients = []
    for name, cat_name in ingredient_names:
        cat = next(c for c in ingredient_categories if c.name == cat_name)
        ingredients.append(
            ingredient_manager.get_or_create(
                name=name,
                defaults={"category": cat},  # matches FK field name
            )
        )

    # ---------- RECIPES ----------
    recipes = []
    for i in range(1, 21):
        # title+category is unique_together, so this is safe for one run;
        # we call repo.delete_all() anyway.
        recipes.append(
            recipe_manager.create(
                title=f"Recipe #{i}",
                category=random.choice(recipe_categories),
                instructions=f"Step 1: Do something.\nStep 2: Finish recipe #{i}.",
            )
        )

    # ---------- RECIPE ITEMS ----------
    # unique_together (recipe, ingredient) => ensure no duplicates per recipe
    for recipe in recipes:
        used_ingredients = random.sample(ingredients, k=random.randint(1, 5))
        for ing in used_ingredients:
            recipe_item_manager.create(
                recipe=recipe,
                ingredient=ing,
                unit=random.choice(units),  # can be null in model, but we set one
                quantity=Decimal(random.randint(50, 300)).quantize(Decimal("0.01")),
            )

    # ---------- COMMENTS ----------
    comments_text = [
        "Very tasty!",
        "Easy to cook.",
        "My kids loved it.",
        "Would cook again.",
        "Needs more salt.",
    ]

    now = timezone.now()

    for _ in range(300):
        # random time within last 14 days
        random_offset = timedelta(
            days=random.randint(0, 30*6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        comment_manager.create(
            recipe=random.choice(recipes),
            user=random.choice(users),
            text=random.choice(comments_text),
            rating=random.choice([3, 4, 5, None]),
            created_at=now - random_offset,
        )

    # ---------- FAVORITES ----------
    # unique_together (recipe, user) => use get_or_create
    favorites_set = set()
    while len(favorites_set) < 20:
        favorites_set.add((random.choice(users).id, random.choice(recipes).id))

    user_by_id = {u.id: u for u in users}
    recipe_by_id = {r.id: r for r in recipes}

    for user_id, recipe_id in favorites_set:
        favorite_manager.get_or_create(
            user=user_by_id[user_id],
            recipe=recipe_by_id[recipe_id],
        )

    print("✅ Database filled successfully")

if __name__ == "__main__":
    main()
