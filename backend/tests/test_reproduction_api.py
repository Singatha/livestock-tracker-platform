from datetime import date, timedelta

import pytest

from apps.animals.models import Animal
from apps.farms.models import Farm
from apps.reproduction.models import BirthRecord, BreedingRecord

pytestmark = pytest.mark.django_db


def headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_create_breeding_calculates_species_gestation(api_client, farm):
    dam = Animal.objects.create(
        farm=farm, ear_tag="EWE-1", species=Animal.Species.SHEEP, sex=Animal.Sex.FEMALE
    )
    sire = Animal.objects.create(
        farm=farm, ear_tag="RAM-1", species=Animal.Species.SHEEP, sex=Animal.Sex.MALE
    )
    response = api_client.post(
        "/api/v1/reproduction/breedings/",
        {
            "dam": str(dam.id),
            "sire": str(sire.id),
            "breeding_date": "2026-07-01",
            "method": "natural",
            "notes": "Observed service",
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 201
    assert response.data["expected_birth_date"] == "2026-11-25"


def test_breeding_rejects_wrong_sex_and_cross_farm_sire(api_client, farm, user):
    dam = Animal.objects.create(farm=farm, ear_tag="EWE-2", species="sheep", sex=Animal.Sex.FEMALE)
    other_farm = Farm.objects.create(name="Other", owner=user)
    sire = Animal.objects.create(
        farm=other_farm, ear_tag="RAM-X", species="sheep", sex=Animal.Sex.MALE
    )
    response = api_client.post(
        "/api/v1/reproduction/breedings/",
        {"dam": str(dam.id), "sire": str(sire.id), "breeding_date": "2026-07-01"},
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400


def test_record_birth_completes_breeding(api_client, farm, user):
    dam = Animal.objects.create(farm=farm, ear_tag="DOE-1", species="goat", sex=Animal.Sex.FEMALE)
    breeding = BreedingRecord.objects.create(
        farm=farm,
        dam=dam,
        breeding_date=date.today() - timedelta(days=150),
        expected_birth_date=date.today(),
        status=BreedingRecord.Status.CONFIRMED,
        recorded_by=user,
    )
    response = api_client.post(
        "/api/v1/reproduction/births/",
        {
            "breeding": str(breeding.id),
            "birth_date": date.today().isoformat(),
            "total_born": 2,
            "born_alive": 2,
            "stillborn": 0,
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 201
    assert BirthRecord.objects.filter(breeding=breeding, dam=dam).exists()
    breeding.refresh_from_db()
    assert breeding.status == BreedingRecord.Status.COMPLETED


def test_birth_counts_must_balance(api_client, farm, user):
    dam = Animal.objects.create(farm=farm, ear_tag="EWE-3", species="sheep", sex=Animal.Sex.FEMALE)
    breeding = BreedingRecord.objects.create(
        farm=farm,
        dam=dam,
        breeding_date=date.today(),
        expected_birth_date=date.today(),
        recorded_by=user,
    )
    response = api_client.post(
        "/api/v1/reproduction/births/",
        {
            "breeding": str(breeding.id),
            "birth_date": date.today().isoformat(),
            "total_born": 3,
            "born_alive": 1,
            "stillborn": 1,
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400


def test_eligible_birth_filter_only_returns_open_breedings(api_client, farm, user):
    dam = Animal.objects.create(
        farm=farm, ear_tag="EWE-OPEN", species="sheep", sex=Animal.Sex.FEMALE
    )
    open_record = BreedingRecord.objects.create(
        farm=farm,
        dam=dam,
        breeding_date=date.today(),
        expected_birth_date=date.today(),
        status=BreedingRecord.Status.CONFIRMED,
        recorded_by=user,
    )
    BreedingRecord.objects.create(
        farm=farm,
        dam=dam,
        breeding_date=date.today(),
        expected_birth_date=date.today(),
        status=BreedingRecord.Status.NOT_PREGNANT,
        recorded_by=user,
    )

    response = api_client.get(
        "/api/v1/reproduction/breedings/?eligible_for_birth=true", **headers(farm)
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [str(open_record.id)]


def test_birth_rejects_closed_breeding(api_client, farm, user):
    dam = Animal.objects.create(
        farm=farm, ear_tag="EWE-CLOSED", species="sheep", sex=Animal.Sex.FEMALE
    )
    breeding = BreedingRecord.objects.create(
        farm=farm,
        dam=dam,
        breeding_date=date.today(),
        expected_birth_date=date.today(),
        status=BreedingRecord.Status.NOT_PREGNANT,
        recorded_by=user,
    )

    response = api_client.post(
        "/api/v1/reproduction/births/",
        {
            "breeding": str(breeding.id),
            "birth_date": date.today().isoformat(),
            "total_born": 1,
            "born_alive": 1,
            "stillborn": 0,
        },
        format="json",
        **headers(farm),
    )

    assert response.status_code == 400
    assert "breeding" in response.data
