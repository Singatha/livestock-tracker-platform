from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.animals.models import Animal
from apps.health.models import HealthObservation
from apps.husbandry.models import HusbandryTask
from apps.nutrition.models import Feed

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_report_overview_summarizes_selected_farm(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="R-1", species="sheep", needs_attention=True)
    HealthObservation.objects.create(
        farm=farm, animal=animal, summary="Monitor appetite", recorded_by=user
    )
    HusbandryTask.objects.create(
        farm=farm,
        title="Overdue check",
        task_type="health_check",
        due_date=timezone.localdate() - timedelta(days=1),
    )
    Feed.objects.create(
        farm=farm,
        name="Hay",
        category="forage",
        quantity_on_hand=Decimal("10"),
        reorder_level=Decimal("15"),
        unit_cost=Decimal("3.50"),
    )

    response = api_client.get("/api/v1/reports/overview/", **farm_headers(farm))

    assert response.status_code == 200
    assert response.data["animals"] == 1
    assert response.data["needs_attention"] == 1
    assert response.data["open_health_concerns"] == 1
    assert response.data["overdue_tasks"] == 1
    assert response.data["low_stock_feeds"] == 1
    assert Decimal(response.data["inventory_value"]) == Decimal("35.00")


def test_animal_csv_honors_species_filter(api_client, farm):
    Animal.objects.create(farm=farm, ear_tag="S-CSV", species="sheep")
    Animal.objects.create(farm=farm, ear_tag="G-CSV", species="goat")

    response = api_client.get("/api/v1/reports/export/animals/?species=sheep", **farm_headers(farm))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert b"S-CSV" in response.content
    assert b"G-CSV" not in response.content


def test_activity_endpoint_returns_monthly_series(api_client, farm):
    Animal.objects.create(farm=farm, ear_tag="TREND-1", species="goat")

    response = api_client.get("/api/v1/reports/activity/", **farm_headers(farm))

    assert response.status_code == 200
    assert response.data[-1]["animals_registered"] == 1
