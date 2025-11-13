from rest_framework import viewsets
from serializers import IngredientSerializer
from Django.cookbook.recipes.API.manage_api import ingredient_manager

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        return ingredient_manager.list(order_by=["name"])

    def perform_create(self, serializer):
        return ingredient_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return ingredient_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return ingredient_manager.delete(instance)