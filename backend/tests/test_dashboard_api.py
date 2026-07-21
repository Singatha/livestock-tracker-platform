import pytest

from apps.animals.models import Animal

pytestmark = pytest.mark.django_db


def test_dashboard_counts_only_active_animals_for_selected_farm(api_client, farm):
    Animal.objects.create(farm=farm, ear_tag="S-1", species="sheep")
    Animal.objects.create(farm=farm, ear_tag="S-2", species="sheep", needs_attention=True)
    Animal.objects.create(farm=farm, ear_tag="G-1", species="goat")
    Animal.objects.create(farm=farm, ear_tag="OLD", species="sheep", status="sold")

    response = api_client.get("/api/v1/dashboard/", HTTP_X_FARM_ID=str(farm.id))

    assert response.status_code == 200
    assert response.data == {"total": 3, "sheep": 2, "goats": 1, "needs_attention": 1}
