from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.animals.models import Animal
from apps.farms.permissions import selected_farm
from apps.health.models import HealthObservation
from apps.husbandry.models import HusbandryTask


class DashboardSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    sheep = serializers.IntegerField()
    goats = serializers.IntegerField()
    needs_attention = serializers.IntegerField()
    open_health_concerns = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    due_next_7_days = serializers.IntegerField()


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
        today = timezone.localdate()
        summary.update(
            open_health_concerns=HealthObservation.objects.filter(
                farm=farm, is_resolved=False
            ).count(),
            overdue_tasks=HusbandryTask.objects.filter(
                farm=farm,
                status=HusbandryTask.Status.SCHEDULED,
                due_date__lt=today,
            ).count(),
            due_next_7_days=HusbandryTask.objects.filter(
                farm=farm,
                status=HusbandryTask.Status.SCHEDULED,
                due_date__range=(today, today + timedelta(days=7)),
            ).count(),
        )
        return Response(summary)
