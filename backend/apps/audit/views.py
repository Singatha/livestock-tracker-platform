from rest_framework.generics import ListAPIView

from apps.farms.permissions import FarmManagerOnlyPermission, selected_farm

from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventListView(ListAPIView):
    serializer_class = AuditEventSerializer
    permission_classes = [FarmManagerOnlyPermission]

    def get_queryset(self):
        queryset = AuditEvent.objects.filter(farm=selected_farm(self.request)).select_related(
            "actor"
        )
        if resource_type := self.request.query_params.get("resource_type"):
            queryset = queryset.filter(resource_type=resource_type)
        if action := self.request.query_params.get("action"):
            queryset = queryset.filter(action=action)
        if actor := self.request.query_params.get("actor"):
            queryset = queryset.filter(actor_id=actor)
        if animal := self.request.query_params.get("animal"):
            queryset = queryset.filter(animal_id=animal)
        if date_from := self.request.query_params.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to := self.request.query_params.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset
