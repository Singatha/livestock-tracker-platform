import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.farms.models import Farm, FarmMembership


@pytest.fixture
def user(db):
    return User.objects.create_user(username="owner", password="test-password")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="outsider", password="test-password")


@pytest.fixture
def farm(user):
    farm = Farm.objects.create(name="Green Valley", owner=user)
    FarmMembership.objects.create(farm=farm, user=user, role=FarmMembership.Role.OWNER)
    return farm


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_login(user)
    return client
