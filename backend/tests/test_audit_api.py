import pytest
from rest_framework.test import APIClient

from apps.audit.models import AuditEvent
from apps.farms.models import FarmMembership

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def create_animal(api_client, farm, ear_tag="AUDIT-1"):
    return api_client.post(
        "/api/v1/animals/",
        {"ear_tag": ear_tag, "species": "sheep", "notes": "Initial note"},
        format="json",
        **farm_headers(farm),
    )


def test_api_mutations_create_immutable_audit_events(api_client, farm, user):
    created = create_animal(api_client, farm)
    assert created.status_code == 201

    updated = api_client.patch(
        f"/api/v1/animals/{created.data['id']}/",
        {"notes": "Checked today"},
        format="json",
        **farm_headers(farm),
    )
    assert updated.status_code == 200

    events = AuditEvent.objects.filter(farm=farm, resource_id=created.data["id"])
    assert events.count() == 2
    creation = events.get(action=AuditEvent.Action.CREATED)
    change = events.get(action=AuditEvent.Action.UPDATED)
    assert creation.actor == user
    assert str(creation.animal_id) == created.data["id"]
    assert change.changes["notes"] == {"from": "Initial note", "to": "Checked today"}

    with pytest.raises(TypeError, match="immutable"):
        change.save()
    with pytest.raises(TypeError, match="immutable"):
        change.delete()


def test_activity_list_is_farm_scoped_and_filterable(api_client, farm):
    create_animal(api_client, farm)

    response = api_client.get(
        "/api/v1/audit/?action=created&resource_type=Animal", **farm_headers(farm)
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["resource_name"] == "AUDIT-1"


def test_worker_cannot_view_activity(farm, other_user):
    FarmMembership.objects.create(farm=farm, user=other_user, role=FarmMembership.Role.WORKER)
    client = APIClient()
    client.force_login(other_user)

    response = client.get("/api/v1/audit/", **farm_headers(farm))

    assert response.status_code == 403


def test_audit_csv_export_contains_farm_activity(api_client, farm):
    create_animal(api_client, farm, "CSV-AUDIT")

    response = api_client.get("/api/v1/reports/export/audit/", **farm_headers(farm))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert b"CSV-AUDIT" in response.content


def test_reproduction_and_treatment_course_exports_are_available(api_client, farm):
    reproduction = api_client.get("/api/v1/reports/export/reproduction/", **farm_headers(farm))
    treatments = api_client.get("/api/v1/reports/export/treatment-courses/", **farm_headers(farm))

    assert reproduction.status_code == 200
    assert b"Breeding date" in reproduction.content
    assert treatments.status_code == 200
    assert b"Meat withdrawal ends" in treatments.content
