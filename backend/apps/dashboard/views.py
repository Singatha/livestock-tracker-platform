from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.animals.models import Animal
from apps.animals.permissions import selected_farm


class DashboardSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    sheep = serializers.IntegerField()
    goats = serializers.IntegerField()
    needs_attention = serializers.IntegerField()


class DashboardSummaryView(APIView):
    @extend_schema(responses=DashboardSummarySerializer)
    def get(self, request):
        farm = selected_farm(request)
        summary = Animal.objects.filter(farm=farm).aggregate(
            total=Count("id", filter=Q(status=Animal.Status.ACTIVE)),
            sheep=Count("id", filter=Q(status=Animal.Status.ACTIVE, species=Animal.Species.SHEEP)),
            goats=Count("id", filter=Q(status=Animal.Status.ACTIVE, species=Animal.Species.GOAT)),
            needs_attention=Count(
                "id", filter=Q(status=Animal.Status.ACTIVE, needs_attention=True)
            ),
        )
        return Response(summary)
