from datetime import timedelta

import pytest
from django.utils import timezone

from apps.animals.models import Animal
from apps.health.models import HealthObservation
from apps.husbandry.models import HusbandryTask

pytestmark = pytest.mark.django_db


def test_dashboard_counts_only_active_animals_for_selected_farm(api_client, farm, user):
    sheep = Animal.objects.create(farm=farm, ear_tag="S-1", species="sheep")
    Animal.objects.create(farm=farm, ear_tag="S-2", species="sheep", needs_attention=True)
    Animal.objects.create(farm=farm, ear_tag="G-1", species="goat")
    Animal.objects.create(farm=farm, ear_tag="OLD", species="sheep", status="sold")
    HealthObservation.objects.create(
        farm=farm, animal=sheep, summary="Limping", severity="medium", recorded_by=user
    )
    HusbandryTask.objects.create(
        farm=farm,
        animal=sheep,
        task_type="hoof_care",
        title="Inspect hoof",
        due_date=timezone.localdate() - timedelta(days=1),
    )
    HusbandryTask.objects.create(
        farm=farm,
        animal=sheep,
        task_type="health_check",
        title="Follow-up check",
        due_date=timezone.localdate() + timedelta(days=3),
    )

    response = api_client.get("/api/v1/dashboard/", HTTP_X_FARM_ID=str(farm.id))

    assert response.status_code == 200
    assert response.data == {
        "total": 3,
        "sheep": 2,
        "goats": 1,
        "needs_attention": 1,
        "open_health_concerns": 1,
        "overdue_tasks": 1,
        "due_next_7_days": 1,
    }
