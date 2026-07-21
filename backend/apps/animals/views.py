from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.farms.viewsets import FarmScopedModelViewSet

from .models import Animal, Flock
from .selectors import animal_timeline
from .serializers import AnimalSerializer, FlockSerializer, TimelineEventSerializer


class FlockViewSet(FarmScopedModelViewSet):
    queryset = Flock.objects.none()
    serializer_class = FlockSerializer

    def get_queryset(self):
        return Flock.objects.filter(farm=self.farm)


class AnimalViewSet(FarmScopedModelViewSet):
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

    @extend_schema(responses=TimelineEventSerializer(many=True))
    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        return Response(animal_timeline(animal=self.get_object()))
