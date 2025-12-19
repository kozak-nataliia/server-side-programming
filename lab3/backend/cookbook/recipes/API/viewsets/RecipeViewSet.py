from rest_framework import viewsets
from recipes.api.serializers import RecipeSerializer
from recipes.api.manage_api import recipe_manager
from recipes.api.permissions import IsAdminOrReadOnly
from rest_framework.pagination import PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    class Pagination(PageNumberPagination):
        page_size = 12
        page_size_query_param = "page_size"  # optional override
        max_page_size = 50

    pagination_class = Pagination

    def get_queryset(self):
        return recipe_manager.list(order_by=["title"])

    def perform_create(self, serializer):
        return recipe_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return recipe_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return recipe_manager.delete(instance)