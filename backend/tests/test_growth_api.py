from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.animals.models import Animal
from apps.farms.models import Farm
from apps.growth.models import WeightMeasurement

pytestmark = pytest.mark.django_db


def headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_worker_can_record_weight(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="W-1", species="sheep")
    response = api_client.post(
        "/api/v1/growth/weights/",
        {
            "animal": str(animal.id),
            "measured_on": "2026-07-22",
            "weight_kg": "42.50",
            "body_condition_score": "3.5",
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 201
    measurement = WeightMeasurement.objects.get(animal=animal)
    assert measurement.weight_kg == Decimal("42.50")
    assert measurement.recorded_by == user


def test_weight_rejects_cross_farm_animal(api_client, farm, user):
    other_farm = Farm.objects.create(name="Other", owner=user)
    animal = Animal.objects.create(farm=other_farm, ear_tag="OTHER-1", species="goat")
    response = api_client.post(
        "/api/v1/growth/weights/",
        {"animal": str(animal.id), "measured_on": "2026-07-22", "weight_kg": "30"},
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400


def test_growth_summary_calculates_change_and_average_daily_gain(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="GAIN-1", species="sheep")
    WeightMeasurement.objects.create(
        farm=farm,
        animal=animal,
        measured_on=date.today() - timedelta(days=10),
        weight_kg="40",
        recorded_by=user,
    )
    WeightMeasurement.objects.create(
        farm=farm,
        animal=animal,
        measured_on=date.today(),
        weight_kg="45",
        recorded_by=user,
    )
    response = api_client.get("/api/v1/growth/summary/", **headers(farm))
    assert response.status_code == 200
    assert response.data[0]["change_kg"] == Decimal("5.00")
    assert response.data[0]["average_daily_gain_kg"] == Decimal("0.500")


def test_only_one_weight_per_animal_per_day(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="ONCE-1", species="goat")
    WeightMeasurement.objects.create(
        farm=farm,
        animal=animal,
        measured_on=date.today(),
        weight_kg="31",
        recorded_by=user,
    )
    response = api_client.post(
        "/api/v1/growth/weights/",
        {"animal": str(animal.id), "measured_on": date.today(), "weight_kg": "32"},
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400
