from rest_framework import viewsets
from recipes.API.serializers import RecipeItemSerializer
from recipes.API.manage_api import recipe_item_manager
from recipes.API.permissions import IsAdminOrReadOnly


class RecipeItemViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeItemSerializer

    def get_queryset(self):
        return recipe_item_manager.list(order_by=["id"])

    def perform_create(self, serializer):
        return recipe_item_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return recipe_item_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return recipe_item_manager.delete(instance)