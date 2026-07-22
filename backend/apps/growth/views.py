from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.farms.permissions import selected_farm
from apps.farms.viewsets import FarmScopedModelViewSet

from .models import WeightMeasurement
from .selectors import animal_growth_summary
from .serializers import AnimalGrowthSummarySerializer, WeightMeasurementSerializer


class WeightMeasurementViewSet(FarmScopedModelViewSet):
    queryset = WeightMeasurement.objects.none()
    serializer_class = WeightMeasurementSerializer

    def get_queryset(self):
        queryset = WeightMeasurement.objects.filter(farm=self.farm).select_related(
            "animal", "recorded_by"
        )
        animal_id = self.request.query_params.get("animal")
        flock_id = self.request.query_params.get("flock")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if flock_id:
            queryset = queryset.filter(animal__flock_id=flock_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, recorded_by=self.request.user)


class GrowthSummaryView(APIView):
    @extend_schema(responses=AnimalGrowthSummarySerializer(many=True))
    def get(self, request):
        return Response(animal_growth_summary(selected_farm(request)))
