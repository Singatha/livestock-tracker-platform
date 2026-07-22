from django.db import models

from apps.farms.viewsets import FarmScopedModelViewSet

from .models import Feed, FeedingPlan
from .serializers import FeedingPlanSerializer, FeedSerializer


class FeedViewSet(FarmScopedModelViewSet):
    serializer_class = FeedSerializer
    queryset = Feed.objects.none()

    def get_queryset(self):
        queryset = Feed.objects.filter(farm=self.farm)
        if self.request.query_params.get("low_stock") == "true":
            queryset = queryset.filter(quantity_on_hand__lte=models.F("reorder_level"))
        return queryset


class FeedingPlanViewSet(FarmScopedModelViewSet):
    serializer_class = FeedingPlanSerializer
    queryset = FeedingPlan.objects.none()

    def get_queryset(self):
        queryset = (
            FeedingPlan.objects.filter(farm=self.farm)
            .select_related("flock")
            .prefetch_related("items__feed")
        )
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(is_active=True)
        return queryset
