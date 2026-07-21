from rest_framework.viewsets import ModelViewSet

from .models import Animal, Flock
from .permissions import FarmRecordPermission
from .serializers import AnimalSerializer, FlockSerializer


class FarmScopedViewSet(ModelViewSet):
    permission_classes = [FarmRecordPermission]
    farm = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.farm = request.selected_farm

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "farm": self.farm}

    def perform_create(self, serializer):
        serializer.save(farm=self.farm)


class FlockViewSet(FarmScopedViewSet):
    queryset = Flock.objects.none()
    serializer_class = FlockSerializer

    def get_queryset(self):
        return Flock.objects.filter(farm=self.farm)


class AnimalViewSet(FarmScopedViewSet):
    queryset = Animal.objects.none()
    serializer_class = AnimalSerializer

    def get_queryset(self):
        queryset = Animal.objects.filter(farm=self.farm).select_related("flock")
        for field in ("species", "status", "sex", "needs_attention"):
            value = self.request.query_params.get(field)
            if value not in (None, ""):
                queryset = queryset.filter(**{field: value})
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(ear_tag__icontains=search)
        return queryset
