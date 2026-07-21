import pytest
from rest_framework.test import APIClient

from apps.animals.models import Animal
from apps.farms.models import FarmMembership
from apps.health.models import HealthObservation, Treatment

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_records_observation_with_current_user(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="S-10", species="sheep")

    response = api_client.post(
        "/api/v1/health/observations/",
        {
            "animal": str(animal.id),
            "category": "injury",
            "severity": "medium",
            "summary": "Limping on front leg",
            "notes": "Observed after returning from pasture",
        },
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 201
    observation = HealthObservation.objects.get(id=response.data["id"])
    assert observation.recorded_by == user
    assert observation.farm == farm


def test_rejects_treatment_for_animal_from_another_farm(api_client, farm, other_user):
    other_farm = farm.__class__.objects.create(name="Other", owner=other_user)
    other_animal = Animal.objects.create(farm=other_farm, ear_tag="OTHER-1", species="sheep")

    response = api_client.post(
        "/api/v1/health/treatments/",
        {"animal": str(other_animal.id), "product": "Recorded product"},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 400
    assert Treatment.objects.count() == 0


def test_viewer_cannot_record_observation(farm, other_user):
    FarmMembership.objects.create(farm=farm, user=other_user, role=FarmMembership.Role.VIEWER)
    animal = Animal.objects.create(farm=farm, ear_tag="S-11", species="sheep")
    client = APIClient()
    client.force_login(other_user)

    response = client.post(
        "/api/v1/health/observations/",
        {"animal": str(animal.id), "summary": "Should not save"},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 403


def test_treatment_observation_must_match_animal(api_client, farm, user):
    first = Animal.objects.create(farm=farm, ear_tag="S-12", species="sheep")
    second = Animal.objects.create(farm=farm, ear_tag="S-13", species="sheep")
    observation = HealthObservation.objects.create(
        farm=farm, animal=first, summary="First animal concern", recorded_by=user
    )

    response = api_client.post(
        "/api/v1/health/treatments/",
        {
            "animal": str(second.id),
            "observation": str(observation.id),
            "product": "Recorded product",
        },
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 400
    assert "observation" in response.data
