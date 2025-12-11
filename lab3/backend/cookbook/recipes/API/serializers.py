from rest_framework import serializers
from recipes.models import (
    IngredientCategory, RecipeCategory, Unit,
    Ingredient, Recipe, RecipeItem
)

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
        
class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = "__all__"

class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = "__all__"

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"

class RecipeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True
    )
    
    class Meta:
        model = Recipe
        fields = "__all__"
        
class RecipeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeItem
        fields = "__all__"
