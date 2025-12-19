from recipes.repos import RepositoryHub
from recipes.services import (
    RecipeCategoryManager, IngredientCategoryManager,
    UnitManager, IngredientManager, RecipeManager, RecipeItemManager,
    RecipeCommentManager, FavoriteRecipeManager,
)
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

hub = RepositoryHub()
recipe_manager = RecipeManager(hub.recipes)
ingredient_manager = IngredientManager(hub.ingredients)
recipe_item_manager = RecipeItemManager(hub.items)
unit_manager = UnitManager(hub.units)
ingredient_cat_manager = IngredientCategoryManager(hub.ingredient_categories)
recipe_cat_manager = RecipeCategoryManager(hub.recipe_categories)
comment_manager = RecipeCommentManager(hub.recipe_comments)   
favorite_manager = FavoriteRecipeManager(hub.favorites)       
User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    Simple registration endpoint.
    Input: { "username": "...", "password": "...", "email": "..." (optional) }
    Output: { "token": "...", "username": "..." }
    """
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    email = (request.data.get("email") or "").strip() or None

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "This username is already taken."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Return info about the currently authenticated user.
    """
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    )

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def recipe_comments_view(request, recipe_id: int):
    """
    GET  → list comments for recipe (public)
    POST → add comment (auth only)
    """
    recipe = recipe_manager.by_id(recipe_id)

    if request.method == "GET":
        comments = comment_manager.for_recipe(recipe)
        data = [
            {
                "id": c.id,
                "user": c.user.username,
                "text": c.text,
                "rating": c.rating,
                "created_at": c.created_at,
            }
            for c in comments
        ]
        return Response(data)

    # POST
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    text = (request.data.get("text") or "").strip()
    rating = request.data.get("rating", None)

    if not text:
        return Response(
            {"detail": "Comment text is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    comment = comment_manager.create(
        recipe=recipe,
        user=request.user,
        text=text,
        rating=rating,
    )
    return Response(
        {
            "id": comment.id,
            "user": comment.user.username,
            "text": comment.text,
            "rating": comment.rating,
            "created_at": comment.created_at,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def comment_detail_view(request, comment_id: int):
    """
    Delete own comment; staff can delete any.
    """
    comment = comment_manager.by_id(comment_id)

    if (request.user != comment.user) and (not request.user.is_staff):
        return Response(
            {"detail": "You do not have permission to delete this comment."},
            status=status.HTTP_403_FORBIDDEN,
        )

    comment_manager.delete(comment)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recipe_toggle_favorite_view(request, recipe_id: int):
    """
    Toggle favorite for current user.
    """
    recipe = recipe_manager.by_id(recipe_id)
    is_favorite = favorite_manager.toggle_favorite(request.user, recipe)
    return Response({"favorite": is_favorite})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_favorites_view(request):
    """
    List recipes favorited by current user.
    """
    favs = favorite_manager.favorites_for_user(request.user)
    data = [
        {
            "recipe_id": f.recipe_id,
            "title": f.recipe.title,
            "added_at": f.created_at,
        }
        for f in favs
    ]
    return Response(data)

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


