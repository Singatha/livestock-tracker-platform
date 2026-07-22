from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.animals.models import Animal
from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask
from apps.nutrition.models import Feed


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def report_filters(request):
    return {
        "date_from": parse_date(request.query_params.get("date_from")),
        "date_to": parse_date(request.query_params.get("date_to")),
        "flock": request.query_params.get("flock") or None,
        "species": request.query_params.get("species") or None,
        "status": request.query_params.get("status") or None,
    }


def filtered_animals(farm, filters):
    queryset = Animal.objects.filter(farm=farm)
    if filters["flock"]:
        queryset = queryset.filter(flock_id=filters["flock"])
    if filters["species"]:
        queryset = queryset.filter(species=filters["species"])
    if filters["status"]:
        queryset = queryset.filter(status=filters["status"])
    if filters["date_from"]:
        queryset = queryset.filter(created_at__date__gte=filters["date_from"])
    if filters["date_to"]:
        queryset = queryset.filter(created_at__date__lte=filters["date_to"])
    return queryset


def report_summary(farm, filters):
    animals = filtered_animals(farm, filters)
    animal_ids = animals.values("id")
    today = timezone.localdate()
    date_from = filters["date_from"] or today - timedelta(days=180)
    date_to = filters["date_to"] or today
    observations = HealthObservation.objects.filter(
        farm=farm, animal_id__in=animal_ids, observed_at__date__range=(date_from, date_to)
    )
    treatments = Treatment.objects.filter(
        farm=farm, animal_id__in=animal_ids, administered_at__date__range=(date_from, date_to)
    )
    tasks = HusbandryTask.objects.filter(farm=farm, due_date__range=(date_from, date_to))
    if filters["flock"]:
        tasks = tasks.filter(Q(flock_id=filters["flock"]) | Q(animal__flock_id=filters["flock"]))
    inventory_value = Feed.objects.filter(farm=farm).aggregate(
        value=Sum(
            ExpressionWrapper(
                F("quantity_on_hand") * F("unit_cost"),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        )
    )["value"] or Decimal("0")
    return {
        "animals": animals.count(),
        "active_animals": animals.filter(status=Animal.Status.ACTIVE).count(),
        "needs_attention": animals.filter(needs_attention=True).count(),
        "health_observations": observations.count(),
        "open_health_concerns": observations.filter(is_resolved=False).count(),
        "treatments": treatments.count(),
        "completed_tasks": tasks.filter(status=HusbandryTask.Status.COMPLETED).count(),
        "overdue_tasks": HusbandryTask.objects.filter(
            farm=farm, status=HusbandryTask.Status.SCHEDULED, due_date__lt=today
        ).count(),
        "low_stock_feeds": Feed.objects.filter(
            farm=farm, quantity_on_hand__lte=F("reorder_level")
        ).count(),
        "inventory_value": inventory_value,
    }


def monthly_activity(farm, filters):
    today = timezone.localdate()
    start = filters["date_from"] or (today.replace(day=1) - timedelta(days=150)).replace(day=1)
    end = filters["date_to"] or today
    animals = filtered_animals(farm, {**filters, "date_from": start, "date_to": end})
    observations = HealthObservation.objects.filter(
        farm=farm, observed_at__date__range=(start, end)
    )
    tasks = HusbandryTask.objects.filter(
        farm=farm,
        status=HusbandryTask.Status.COMPLETED,
        completed_at__date__range=(start, end),
    )
    series = {}
    for name, queryset, field in [
        ("animals_registered", animals, "created_at"),
        ("health_observations", observations, "observed_at"),
        ("tasks_completed", tasks, "completed_at"),
    ]:
        values = (
            queryset.annotate(month=TruncMonth(field)).values("month").annotate(count=Count("id"))
        )
        for value in values:
            key = value["month"].date().isoformat()
            series.setdefault(
                key,
                {
                    "month": key,
                    "animals_registered": 0,
                    "health_observations": 0,
                    "tasks_completed": 0,
                },
            )[name] = value["count"]
    return [series[key] for key in sorted(series)]
