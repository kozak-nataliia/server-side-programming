from rest_framework import viewsets
from serializers import UnitSerializer
from managers_api import unit_manager

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer

    def get_queryset(self):
        return unit_manager.list(order_by=["name"])

    def perform_create(self, serializer):
        return unit_manager.create(**serializer.validated_data)

    def perform_update(self, serializer):
        obj = self.get_object()
        return unit_manager.update(obj, **serializer.validated_data)

    def perform_destroy(self, instance):
        return unit_manager.delete(instance)