from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.farms.models import FarmMembership
from apps.farms.viewsets import FarmScopedModelViewSet

from .models import Animal, AnimalLifecycleEvent, Flock
from .selectors import animal_timeline
from .serializers import (
    AnimalLifecycleEventSerializer,
    AnimalSerializer,
    ChangeAnimalStatusSerializer,
    FlockSerializer,
    TimelineEventSerializer,
    TransferAnimalSerializer,
)
from .services import change_animal_status, register_lifecycle_event, transfer_animal


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

    def perform_create(self, serializer):
        animal = serializer.save(farm=self.farm)
        register_lifecycle_event(animal=animal, recorded_by=self.request.user)

    def require_lifecycle_manager(self):
        allowed = FarmMembership.objects.filter(
            farm=self.farm,
            user=self.request.user,
            is_active=True,
            role__in=[FarmMembership.Role.OWNER, FarmMembership.Role.MANAGER],
        ).exists()
        if not allowed:
            raise PermissionDenied("Only farm owners and managers can change animal lifecycle")

    @extend_schema(request=ChangeAnimalStatusSerializer, responses=AnimalSerializer)
    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        self.require_lifecycle_manager()
        serializer = ChangeAnimalStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            animal = change_animal_status(
                animal=self.get_object(), recorded_by=request.user, **serializer.validated_data
            )
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(AnimalSerializer(animal, context=self.get_serializer_context()).data)

    @extend_schema(request=TransferAnimalSerializer, responses=AnimalSerializer)
    @action(detail=True, methods=["post"], url_path="transfer-flock")
    def transfer_flock(self, request, pk=None):
        self.require_lifecycle_manager()
        serializer = TransferAnimalSerializer(
            data=request.data, context={**self.get_serializer_context(), "farm": self.farm}
        )
        serializer.is_valid(raise_exception=True)
        try:
            animal = transfer_animal(
                animal=self.get_object(), recorded_by=request.user, **serializer.validated_data
            )
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(AnimalSerializer(animal, context=self.get_serializer_context()).data)

    @extend_schema(responses=AnimalLifecycleEventSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="lifecycle-events")
    def lifecycle_events(self, request, pk=None):
        events = AnimalLifecycleEvent.objects.filter(animal=self.get_object()).select_related(
            "from_flock", "to_flock", "recorded_by"
        )
        return Response(AnimalLifecycleEventSerializer(events, many=True).data)

    @extend_schema(responses=TimelineEventSerializer(many=True))
    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        return Response(animal_timeline(animal=self.get_object()))
