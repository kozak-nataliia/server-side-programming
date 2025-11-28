from rest_framework import viewsets
from recipes.API.serializers import RecipeSerializer
from recipes.API.manage_api import recipe_manager
from rest_framework.permissions import AllowAny

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return recipe_manager.list(order_by=["title"])

    def perform_create(self, serializer):
        return recipe_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return recipe_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return recipe_manager.delete(instance)