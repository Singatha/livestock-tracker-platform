import pytest

from apps.farms.models import Farm, FarmMembership

pytestmark = pytest.mark.django_db


def test_creating_farm_makes_user_the_owner(api_client, user):
    response = api_client.post("/api/v1/farms/", {"name": "Hill Farm"}, format="json")

    assert response.status_code == 201
    farm = Farm.objects.get(id=response.data["id"])
    assert farm.owner == user
    assert FarmMembership.objects.filter(
        farm=farm, user=user, role=FarmMembership.Role.OWNER
    ).exists()


def test_farm_list_excludes_farms_without_membership(api_client, other_user):
    Farm.objects.create(name="Private Farm", owner=other_user)

    response = api_client.get("/api/v1/farms/")

    assert response.status_code == 200
    assert response.data["results"] == []


def test_viewer_cannot_update_farm(api_client, farm, user):
    membership = FarmMembership.objects.get(farm=farm, user=user)
    membership.role = FarmMembership.Role.VIEWER
    membership.save(update_fields=["role"])

    response = api_client.patch(f"/api/v1/farms/{farm.id}/", {"name": "Changed"}, format="json")

    assert response.status_code == 403
