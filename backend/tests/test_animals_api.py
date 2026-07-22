import pytest
from rest_framework.test import APIClient

from apps.animals.models import Animal, AnimalLifecycleEvent, Flock
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
    assert AnimalLifecycleEvent.objects.filter(
        animal_id=response.data["id"], event_type=AnimalLifecycleEvent.EventType.REGISTERED
    ).exists()


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


def test_owner_can_change_status_with_auditable_event(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="SALE-1", species="sheep")
    response = api_client.post(
        f"/api/v1/animals/{animal.id}/change-status/",
        {
            "status": "sold",
            "effective_date": "2026-07-20",
            "reason": "Sold at auction",
        },
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 200
    animal.refresh_from_db()
    assert animal.status == Animal.Status.SOLD
    event = animal.lifecycle_events.get(event_type=AnimalLifecycleEvent.EventType.STATUS_CHANGED)
    assert event.from_status == Animal.Status.ACTIVE
    assert event.to_status == Animal.Status.SOLD
    assert event.recorded_by == user


def test_owner_can_transfer_active_animal_between_flocks(api_client, farm):
    old_flock = Flock.objects.create(farm=farm, name="Old flock")
    new_flock = Flock.objects.create(farm=farm, name="New flock")
    animal = Animal.objects.create(farm=farm, flock=old_flock, ear_tag="MOVE-1", species="goat")
    response = api_client.post(
        f"/api/v1/animals/{animal.id}/transfer-flock/",
        {"flock": str(new_flock.id), "effective_date": "2026-07-21", "reason": "Regrouped"},
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 200
    animal.refresh_from_db()
    assert animal.flock == new_flock
    assert animal.lifecycle_events.filter(
        event_type=AnimalLifecycleEvent.EventType.FLOCK_TRANSFERRED,
        from_flock=old_flock,
        to_flock=new_flock,
    ).exists()


def test_ordinary_patch_cannot_bypass_lifecycle_actions(api_client, farm):
    animal = Animal.objects.create(farm=farm, ear_tag="SAFE-1", species="sheep")
    response = api_client.patch(
        f"/api/v1/animals/{animal.id}/",
        {"status": "deceased"},
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 400
    animal.refresh_from_db()
    assert animal.status == Animal.Status.ACTIVE


def test_worker_cannot_change_lifecycle(farm, other_user):
    FarmMembership.objects.create(farm=farm, user=other_user, role=FarmMembership.Role.WORKER)
    animal = Animal.objects.create(farm=farm, ear_tag="WORKER-1", species="sheep")
    client = APIClient()
    client.force_login(other_user)
    response = client.post(
        f"/api/v1/animals/{animal.id}/change-status/",
        {"status": "sold", "effective_date": "2026-07-20", "reason": "Attempted"},
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 403
