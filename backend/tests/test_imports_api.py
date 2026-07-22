import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.animals.models import Animal, AnimalLifecycleEvent, Flock
from apps.farms.models import FarmMembership
from apps.imports.models import ImportJob

pytestmark = pytest.mark.django_db


def headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def upload_csv(client, farm, *, kind, mode, content):
    return client.post(
        "/api/v1/imports/preview/",
        {
            "kind": kind,
            "mode": mode,
            "file": SimpleUploadedFile("records.csv", content.encode(), content_type="text/csv"),
        },
        format="multipart",
        **headers(farm),
    )


def test_preview_and_commit_flock_import(api_client, farm):
    response = upload_csv(
        api_client,
        farm,
        kind="flocks",
        mode="all_or_nothing",
        content="name,description\nEwes,Breeding flock\nRams,Breeding males\n",
    )
    assert response.status_code == 201
    assert response.data["valid_rows"] == 2
    commit = api_client.post(
        f"/api/v1/imports/{response.data['id']}/commit/", {}, format="json", **headers(farm)
    )
    assert commit.status_code == 200
    assert commit.data["rows_succeeded"] == 2
    assert Flock.objects.filter(farm=farm).count() == 2


def test_partial_animal_import_skips_invalid_rows_and_records_lifecycle(api_client, farm):
    Flock.objects.create(farm=farm, name="Main")
    content = (
        "ear_tag,name,species,breed,sex,date_of_birth,flock,status,needs_attention,notes\n"
        "S-100,Ada,sheep,Dorper,female,2025-01-01,Main,active,false,Imported\n"
        "S-101,Bad,llama,,female,,Main,active,false,Invalid species\n"
    )
    preview = upload_csv(api_client, farm, kind="animals", mode="partial", content=content)
    assert preview.status_code == 201
    assert preview.data["valid_rows"] == 1
    assert preview.data["rows_failed"] == 1
    commit = api_client.post(
        f"/api/v1/imports/{preview.data['id']}/commit/", {}, format="json", **headers(farm)
    )
    assert commit.status_code == 200
    animal = Animal.objects.get(farm=farm, ear_tag="S-100")
    assert commit.data["rows_succeeded"] == 1
    assert AnimalLifecycleEvent.objects.filter(
        animal=animal, event_type=AnimalLifecycleEvent.EventType.REGISTERED
    ).exists()


def test_all_or_nothing_import_with_errors_cannot_commit(api_client, farm):
    content = (
        "ear_tag,name,species,breed,sex,date_of_birth,flock,status,needs_attention,notes\n"
        "S-200,Valid,sheep,,female,,,active,false,\n"
        "S-201,Invalid,cow,,female,,,active,false,\n"
    )
    preview = upload_csv(api_client, farm, kind="animals", mode="all_or_nothing", content=content)
    commit = api_client.post(
        f"/api/v1/imports/{preview.data['id']}/commit/", {}, format="json", **headers(farm)
    )
    assert commit.status_code == 400
    assert not Animal.objects.filter(farm=farm, ear_tag="S-200").exists()


def test_import_template_has_expected_headers(api_client, farm):
    response = api_client.get("/api/v1/imports/templates/weights/", **headers(farm))
    assert response.status_code == 200
    assert response.content.decode().startswith("ear_tag,measured_on,weight_kg")


def test_worker_cannot_create_bulk_import(farm, other_user):
    FarmMembership.objects.create(farm=farm, user=other_user, role=FarmMembership.Role.WORKER)
    client = APIClient()
    client.force_login(other_user)
    response = upload_csv(
        client,
        farm,
        kind="flocks",
        mode="partial",
        content="name,description\nWorkers,Denied\n",
    )
    assert response.status_code == 403
    assert ImportJob.objects.count() == 0
