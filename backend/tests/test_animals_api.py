import pytest
from rest_framework.test import APIClient

from apps.animals.models import Animal, Flock
from apps.farms.models import Farm, FarmMembership

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_worker_can_register_animal(api_client, farm):
    flock = Flock.objects.create(farm=farm, name="Ewes")

    response = api_client.post(
        "/api/v1/animals/",
        {"ear_tag": "ZA-001", "species": "sheep", "sex": "female", "flock": str(flock.id)},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 201
    assert Animal.objects.filter(farm=farm, ear_tag="ZA-001").exists()


def test_animal_list_is_scoped_to_selected_farm(api_client, farm, user):
    other_farm = Farm.objects.create(name="Second Farm", owner=user)
    FarmMembership.objects.create(farm=other_farm, user=user, role=FarmMembership.Role.OWNER)
    Animal.objects.create(farm=farm, ear_tag="VISIBLE", species=Animal.Species.SHEEP)
    Animal.objects.create(farm=other_farm, ear_tag="HIDDEN", species=Animal.Species.GOAT)

    response = api_client.get("/api/v1/animals/", **farm_headers(farm))

    assert response.status_code == 200
    assert [item["ear_tag"] for item in response.data["results"]] == ["VISIBLE"]


def test_ear_tag_must_be_unique_within_farm(api_client, farm):
    Animal.objects.create(farm=farm, ear_tag="ZA-001", species=Animal.Species.SHEEP)

    response = api_client.post(
        "/api/v1/animals/",
        {"ear_tag": "za-001", "species": "sheep"},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 400
    assert "ear_tag" in response.data


def test_viewer_cannot_register_animal(farm, other_user):
    FarmMembership.objects.create(farm=farm, user=other_user, role=FarmMembership.Role.VIEWER)
    client = APIClient()
    client.force_login(other_user)

    response = client.post(
        "/api/v1/animals/",
        {"ear_tag": "ZA-002", "species": "sheep"},
        format="json",
        **farm_headers(farm),
    )

    assert response.status_code == 403
