from apps.farms.viewsets import FarmScopedModelViewSet

from .models import HealthObservation, Treatment
from .serializers import HealthObservationSerializer, TreatmentSerializer


class HealthObservationViewSet(FarmScopedModelViewSet):
    queryset = HealthObservation.objects.none()
    serializer_class = HealthObservationSerializer

    def get_queryset(self):
        queryset = HealthObservation.objects.filter(farm=self.farm).select_related(
            "animal", "recorded_by"
        )
        animal_id = self.request.query_params.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        resolved = self.request.query_params.get("is_resolved")
        if resolved in {"true", "false"}:
            queryset = queryset.filter(is_resolved=resolved == "true")
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, recorded_by=self.request.user)


class TreatmentViewSet(FarmScopedModelViewSet):
    queryset = Treatment.objects.none()
    serializer_class = TreatmentSerializer

    def get_queryset(self):
        queryset = Treatment.objects.filter(farm=self.farm).select_related(
            "animal", "observation", "administered_by"
        )
        animal_id = self.request.query_params.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, administered_by=self.request.user)
