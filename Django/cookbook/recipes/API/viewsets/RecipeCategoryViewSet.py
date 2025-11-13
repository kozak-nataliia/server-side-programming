from rest_framework import viewsets
from serializers import RecipeCategorySerializer
from managers_api import recipe_cat_manager

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeCategorySerializer

    def get_queryset(self):
        return recipe_cat_manager.list(order_by=["name"])

    def perform_create(self, serializer):
        return recipe_cat_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return recipe_cat_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return recipe_cat_manager.delete(instance)