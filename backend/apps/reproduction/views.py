from apps.farms.viewsets import FarmScopedModelViewSet

from .models import BirthRecord, BreedingRecord
from .serializers import BirthRecordSerializer, BreedingRecordSerializer


class BreedingRecordViewSet(FarmScopedModelViewSet):
    queryset = BreedingRecord.objects.none()
    serializer_class = BreedingRecordSerializer

    def get_queryset(self):
        queryset = BreedingRecord.objects.filter(farm=self.farm).select_related(
            "dam", "sire", "recorded_by"
        )
        animal_id = self.request.query_params.get("animal")
        status = self.request.query_params.get("status")
        if animal_id:
            queryset = queryset.filter(dam_id=animal_id) | queryset.filter(sire_id=animal_id)
        if status:
            queryset = queryset.filter(status=status)
        if self.request.query_params.get("eligible_for_birth") == "true":
            queryset = queryset.filter(
                status__in=[BreedingRecord.Status.EXPOSED, BreedingRecord.Status.CONFIRMED]
            ).filter(birth_record__isnull=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, recorded_by=self.request.user)


class BirthRecordViewSet(FarmScopedModelViewSet):
    queryset = BirthRecord.objects.none()
    serializer_class = BirthRecordSerializer

    def get_queryset(self):
        queryset = BirthRecord.objects.filter(farm=self.farm).select_related(
            "breeding", "dam", "recorded_by"
        )
        animal_id = self.request.query_params.get("animal")
        if animal_id:
            queryset = queryset.filter(dam_id=animal_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, recorded_by=self.request.user)
