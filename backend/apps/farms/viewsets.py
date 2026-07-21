from rest_framework.viewsets import ModelViewSet

from .permissions import FarmRecordPermission


class FarmScopedModelViewSet(ModelViewSet):
    permission_classes = [FarmRecordPermission]
    farm = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.farm = request.selected_farm

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "farm": self.farm}

    def perform_create(self, serializer):
        serializer.save(farm=self.farm)
