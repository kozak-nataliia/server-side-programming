from rest_framework import viewsets
from recipes.API.serializers import UnitSerializer
from recipes.API.manage_api import unit_manager
from recipes.API.permissions import IsAdminOrReadOnly


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return unit_manager.list(order_by=["id"])

    def perform_create(self, serializer):
        return unit_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return unit_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return unit_manager.delete(instance)