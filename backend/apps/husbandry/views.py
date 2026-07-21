from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.farms.viewsets import FarmScopedModelViewSet

from .models import HusbandryTask
from .serializers import CompleteTaskSerializer, HusbandryTaskSerializer
from .services import complete_task


class HusbandryTaskViewSet(FarmScopedModelViewSet):
    queryset = HusbandryTask.objects.none()
    serializer_class = HusbandryTaskSerializer

    def get_queryset(self):
        queryset = HusbandryTask.objects.filter(farm=self.farm).select_related(
            "animal", "flock", "completed_by"
        )
        animal_id = self.request.query_params.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        task_status = self.request.query_params.get("status")
        if task_status:
            queryset = queryset.filter(status=task_status)
        due = self.request.query_params.get("due")
        if due == "overdue":
            queryset = queryset.filter(
                status=HusbandryTask.Status.SCHEDULED, due_date__lt=timezone.localdate()
            )
        return queryset

    @extend_schema(
        request=CompleteTaskSerializer,
        responses={200: HusbandryTaskSerializer},
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        serializer = CompleteTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            complete_task(
                task=task,
                completed_by=request.user,
                completion_notes=serializer.validated_data["completion_notes"],
            )
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_409_CONFLICT)
        return Response(self.get_serializer(task).data)
