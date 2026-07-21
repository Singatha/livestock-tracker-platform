from datetime import timedelta

import pytest
from django.utils import timezone

from apps.animals.models import Animal
from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_completing_recurring_task_creates_next_occurrence(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="S-20", species="sheep")
    due_date = timezone.localdate()
    task = HusbandryTask.objects.create(
        farm=farm,
        animal=animal,
        task_type="health_check",
        title="Routine health check",
        due_date=due_date,
        recurrence_days=30,
    )

    response = api_client.post(
        f"/api/v1/husbandry/tasks/{task.id}/complete/",
        {"completion_notes": "No concerns observed"},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 200
    task.refresh_from_db()
    assert task.status == HusbandryTask.Status.COMPLETED
    assert task.completed_by == user
    assert HusbandryTask.objects.filter(
        farm=farm,
        animal=animal,
        status=HusbandryTask.Status.SCHEDULED,
        due_date=due_date + timedelta(days=30),
    ).exists()


def test_cannot_complete_task_twice(api_client, farm):
    task = HusbandryTask.objects.create(
        farm=farm,
        task_type="shearing",
        title="Annual shearing",
        due_date=timezone.localdate(),
        status=HusbandryTask.Status.COMPLETED,
    )

    response = api_client.post(
        f"/api/v1/husbandry/tasks/{task.id}/complete/",
        {},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 409


def test_animal_timeline_combines_health_treatment_and_tasks(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="S-21", species="sheep")
    observation = HealthObservation.objects.create(
        farm=farm, animal=animal, summary="Reduced appetite", recorded_by=user
    )
    Treatment.objects.create(
        farm=farm,
        animal=animal,
        observation=observation,
        product="Recorded treatment",
        administered_by=user,
    )
    HusbandryTask.objects.create(
        farm=farm,
        animal=animal,
        task_type="health_check",
        title="Follow up",
        due_date=timezone.localdate(),
    )

    response = api_client.get(f"/api/v1/animals/{animal.id}/timeline/", **farm_headers(farm))

    assert response.status_code == 200
    assert {event["kind"] for event in response.data} == {
        "observation",
        "treatment",
        "task",
    }
