from io import StringIO

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.animals.models import Animal, AnimalLifecycleEvent, Flock
from apps.farms.models import Farm, FarmMembership
from apps.growth.models import WeightMeasurement
from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask
from apps.medicine.models import (
    DoseAdministration,
    MedicineBatch,
    MedicineProduct,
    TreatmentCourse,
)
from apps.notifications.models import Notification
from apps.nutrition.models import Feed, FeedingPlan, FeedingPlanItem
from apps.reproduction.models import BirthRecord, BreedingRecord


@pytest.mark.django_db
def test_seed_demo_data_creates_complete_repeatable_demo_farm():
    output = StringIO()

    call_command("seed_demo_data", stdout=output)
    call_command("seed_demo_data", stdout=output)

    owner = User.objects.get(username="demo")
    farm = Farm.objects.get(owner=owner, name="Sunrise Smallholding")

    assert owner.check_password("demo-password")
    assert FarmMembership.objects.filter(farm=farm, is_active=True).count() == 2
    assert Flock.objects.filter(farm=farm).count() == 3
    assert Animal.objects.filter(farm=farm).count() == 11
    assert AnimalLifecycleEvent.objects.filter(farm=farm).count() == 11
    assert WeightMeasurement.objects.filter(farm=farm).count() == 18
    assert HealthObservation.objects.filter(farm=farm).count() == 3
    assert Treatment.objects.filter(farm=farm).count() == 2
    assert BreedingRecord.objects.filter(farm=farm).count() == 3
    assert BirthRecord.objects.filter(farm=farm).count() == 1
    assert MedicineProduct.objects.filter(farm=farm).count() == 2
    assert MedicineBatch.objects.filter(farm=farm).count() == 2
    assert TreatmentCourse.objects.filter(farm=farm).count() == 1
    assert DoseAdministration.objects.filter(farm=farm).count() == 1
    assert Feed.objects.filter(farm=farm).count() == 3
    assert FeedingPlan.objects.filter(farm=farm).count() == 1
    assert FeedingPlanItem.objects.filter(plan__farm=farm).count() == 3
    assert HusbandryTask.objects.filter(farm=farm).count() == 5
    assert Notification.objects.filter(farm=farm).count() == 4
    assert "Login: demo / demo-password" in output.getvalue()


@pytest.mark.django_db
def test_seed_demo_data_supports_custom_credentials():
    call_command("seed_demo_data", username="local-demo", password="local-secret")

    user = User.objects.get(username="local-demo")

    assert user.check_password("local-secret")
    assert Farm.objects.filter(owner=user, name="Sunrise Smallholding").exists()
