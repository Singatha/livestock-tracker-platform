import csv

from django.db.models import Q
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.farms.permissions import FarmManagerOnlyPermission, selected_farm
from apps.growth.models import WeightMeasurement
from apps.health.models import HealthObservation
from apps.husbandry.models import HusbandryTask
from apps.medicine.models import MedicineBatch, TreatmentCourse
from apps.nutrition.models import Feed
from apps.reproduction.models import BreedingRecord

from .renderers import CSVRenderer
from .selectors import filtered_animals, monthly_activity, report_filters, report_summary


class ReportSummarySerializer(serializers.Serializer):
    animals = serializers.IntegerField()
    active_animals = serializers.IntegerField()
    needs_attention = serializers.IntegerField()
    health_observations = serializers.IntegerField()
    open_health_concerns = serializers.IntegerField()
    treatments = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    low_stock_feeds = serializers.IntegerField()
    inventory_value = serializers.DecimalField(max_digits=16, decimal_places=2)


class MonthlyActivitySerializer(serializers.Serializer):
    month = serializers.DateField()
    animals_registered = serializers.IntegerField()
    health_observations = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()


class ReportsOverviewView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(responses=ReportSummarySerializer)
    def get(self, request):
        farm = selected_farm(request)
        return Response(report_summary(farm, report_filters(request)))


class ReportsActivityView(APIView):
    permission_classes = [FarmManagerOnlyPermission]

    @extend_schema(responses=MonthlyActivitySerializer(many=True))
    def get(self, request):
        farm = selected_farm(request)
        return Response(monthly_activity(farm, report_filters(request)))


class ReportsExportView(APIView):
    permission_classes = [FarmManagerOnlyPermission]
    renderer_classes = [CSVRenderer]

    @extend_schema(responses={(200, "text/csv"): OpenApiTypes.BINARY})
    def get(self, request, report_type):
        farm = selected_farm(request)
        filters = report_filters(request)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{report_type}-report.csv"'
        writer = csv.writer(response)
        if report_type == "animals":
            writer.writerow(
                ["Ear tag", "Name", "Species", "Breed", "Sex", "Status", "Flock", "Needs attention"]
            )
            rows = filtered_animals(farm, filters).select_related("flock")
            writer.writerows(
                (
                    item.ear_tag,
                    item.name,
                    item.species,
                    item.breed,
                    item.sex,
                    item.status,
                    item.flock.name if item.flock else "",
                    item.needs_attention,
                )
                for item in rows
            )
        elif report_type == "health":
            writer.writerow(["Observed", "Ear tag", "Category", "Severity", "Summary", "Resolved"])
            rows = HealthObservation.objects.filter(farm=farm).select_related("animal")
            if filters["date_from"]:
                rows = rows.filter(observed_at__date__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(observed_at__date__lte=filters["date_to"])
            if filters["flock"]:
                rows = rows.filter(animal__flock_id=filters["flock"])
            if filters["species"]:
                rows = rows.filter(animal__species=filters["species"])
            if filters["status"]:
                rows = rows.filter(animal__status=filters["status"])
            writer.writerows(
                (
                    item.observed_at.date(),
                    item.animal.ear_tag,
                    item.category,
                    item.severity,
                    item.summary,
                    item.is_resolved,
                )
                for item in rows
            )
        elif report_type == "tasks":
            writer.writerow(["Due date", "Type", "Title", "Status", "Animal", "Flock"])
            rows = HusbandryTask.objects.filter(farm=farm).select_related("animal", "flock")
            if filters["date_from"]:
                rows = rows.filter(due_date__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(due_date__lte=filters["date_to"])
            if filters["flock"]:
                rows = rows.filter(
                    Q(flock_id=filters["flock"]) | Q(animal__flock_id=filters["flock"])
                )
            if filters["species"]:
                rows = rows.filter(animal__species=filters["species"])
            if filters["status"]:
                rows = rows.filter(animal__status=filters["status"])
            writer.writerows(
                (
                    item.due_date,
                    item.task_type,
                    item.title,
                    item.status,
                    item.animal.ear_tag if item.animal else "",
                    item.flock.name if item.flock else "",
                )
                for item in rows
            )
        elif report_type == "feed":
            writer.writerow(
                [
                    "Feed",
                    "Category",
                    "Suitable for",
                    "Quantity",
                    "Unit",
                    "Reorder level",
                    "Unit cost",
                ]
            )
            rows = Feed.objects.filter(farm=farm)
            writer.writerows(
                (
                    item.name,
                    item.category,
                    item.suitability,
                    item.quantity_on_hand,
                    item.unit,
                    item.reorder_level,
                    item.unit_cost or "",
                )
                for item in rows
            )
        elif report_type == "weights":
            writer.writerow(
                ["Date", "Ear tag", "Animal", "Flock", "Weight kg", "Body condition", "Notes"]
            )
            rows = WeightMeasurement.objects.filter(farm=farm).select_related(
                "animal", "animal__flock"
            )
            if filters["date_from"]:
                rows = rows.filter(measured_on__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(measured_on__lte=filters["date_to"])
            if filters["flock"]:
                rows = rows.filter(animal__flock_id=filters["flock"])
            if filters["species"]:
                rows = rows.filter(animal__species=filters["species"])
            writer.writerows(
                (
                    item.measured_on,
                    item.animal.ear_tag,
                    item.animal.name,
                    item.animal.flock.name if item.animal.flock else "",
                    item.weight_kg,
                    item.body_condition_score or "",
                    item.notes,
                )
                for item in rows
            )
        elif report_type == "medicine":
            writer.writerow(["Product", "Active ingredient", "Batch", "Expiry", "Quantity", "Unit"])
            rows = MedicineBatch.objects.filter(farm=farm).select_related("product")
            writer.writerows(
                (
                    item.product.name,
                    item.product.active_ingredient,
                    item.batch_number,
                    item.expiry_date,
                    item.quantity_on_hand,
                    item.product.stock_unit,
                )
                for item in rows
            )
        elif report_type == "reproduction":
            writer.writerow(
                [
                    "Breeding date",
                    "Dam",
                    "Sire",
                    "Method",
                    "Status",
                    "Expected birth",
                    "Birth date",
                    "Born alive",
                    "Stillborn",
                ]
            )
            rows = BreedingRecord.objects.filter(farm=farm).select_related(
                "dam", "sire", "birth_record"
            )
            if filters["date_from"]:
                rows = rows.filter(breeding_date__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(breeding_date__lte=filters["date_to"])
            if filters["flock"]:
                rows = rows.filter(dam__flock_id=filters["flock"])
            if filters["species"]:
                rows = rows.filter(dam__species=filters["species"])
            writer.writerows(
                (
                    item.breeding_date,
                    item.dam.ear_tag,
                    item.sire.ear_tag if item.sire else "",
                    item.method,
                    item.status,
                    item.expected_birth_date,
                    item.birth_record.birth_date if hasattr(item, "birth_record") else "",
                    item.birth_record.born_alive if hasattr(item, "birth_record") else "",
                    item.birth_record.stillborn if hasattr(item, "birth_record") else "",
                )
                for item in rows
            )
        elif report_type == "treatment-courses":
            writer.writerow(
                [
                    "Started",
                    "Ear tag",
                    "Product",
                    "Reason",
                    "Dosage",
                    "Route",
                    "Status",
                    "Meat withdrawal ends",
                    "Milk withdrawal ends",
                ]
            )
            rows = TreatmentCourse.objects.filter(farm=farm).select_related("animal", "product")
            if filters["date_from"]:
                rows = rows.filter(started_on__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(started_on__lte=filters["date_to"])
            if filters["flock"]:
                rows = rows.filter(animal__flock_id=filters["flock"])
            if filters["species"]:
                rows = rows.filter(animal__species=filters["species"])
            writer.writerows(
                (
                    item.started_on,
                    item.animal.ear_tag,
                    item.product.name,
                    item.reason,
                    item.dosage,
                    item.route,
                    item.status,
                    item.meat_withdrawal_end_date or "",
                    item.milk_withdrawal_end_date or "",
                )
                for item in rows
            )
        elif report_type == "audit":
            writer.writerow(
                ["Timestamp", "Actor", "Action", "Resource type", "Resource", "Resource ID"]
            )
            rows = AuditEvent.objects.filter(farm=farm).select_related("actor")
            if filters["date_from"]:
                rows = rows.filter(created_at__date__gte=filters["date_from"])
            if filters["date_to"]:
                rows = rows.filter(created_at__date__lte=filters["date_to"])
            writer.writerows(
                (
                    item.created_at.isoformat(),
                    (item.actor.get_full_name() or item.actor.email or item.actor.username)
                    if item.actor
                    else "Former user",
                    item.action,
                    item.resource_type,
                    item.resource_name,
                    item.resource_id,
                )
                for item in rows
            )
        else:
            response.status_code = 404
        return response
