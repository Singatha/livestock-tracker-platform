from datetime import date

import pytest

from apps.animals.models import Animal, Flock
from apps.nutrition.models import Feed

pytestmark = pytest.mark.django_db


def farm_headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def test_creates_feed_and_reports_low_stock(api_client, farm):
    response = api_client.post(
        "/api/v1/nutrition/feeds/",
        {
            "name": "Lucerne hay",
            "category": "forage",
            "suitability": "both",
            "unit": "kg",
            "quantity_on_hand": "20.00",
            "reorder_level": "25.00",
        },
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 201
    assert response.data["is_low_stock"] is True


def test_creates_plan_with_farm_owned_feed(api_client, farm):
    flock = Flock.objects.create(farm=farm, name="Ewes")
    feed = Feed.objects.create(farm=farm, name="Pasture", category="forage")
    response = api_client.post(
        "/api/v1/nutrition/plans/",
        {
            "flock": str(flock.id),
            "name": "Maintenance plan",
            "life_stage": "maintenance",
            "start_date": date.today().isoformat(),
            "items": [{"feed": str(feed.id), "quantity_per_animal": "1.500"}],
        },
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 201
    assert response.data["items"][0]["feed_name"] == "Pasture"


def test_plan_warns_when_feed_is_not_suitable_for_flock_species(api_client, farm):
    flock = Flock.objects.create(farm=farm, name="Goats")
    Animal.objects.create(farm=farm, flock=flock, ear_tag="G-1", species="goat")
    feed = Feed.objects.create(
        farm=farm, name="Sheep mineral", category="mineral", suitability="sheep"
    )
    response = api_client.post(
        "/api/v1/nutrition/plans/",
        {
            "flock": str(flock.id),
            "name": "Review plan",
            "life_stage": "maintenance",
            "start_date": date.today().isoformat(),
            "items": [{"feed": str(feed.id), "quantity_per_animal": "0.010"}],
        },
        format="json",
        **farm_headers(farm),
    )
    assert response.status_code == 201
    assert response.data["compatibility_warnings"]
