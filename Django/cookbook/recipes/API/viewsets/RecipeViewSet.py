from rest_framework import viewsets
from serializers import RecipeSerializer
from managers_api import recipe_manager

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return recipe_manager.list(order_by=["name"])

    def perform_create(self, serializer):
        return recipe_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return recipe_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return recipe_manager.delete(instance)