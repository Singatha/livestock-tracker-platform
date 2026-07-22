from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from apps.animals.models import Animal
from apps.farms.models import Farm
from apps.medicine.models import DoseAdministration, MedicineBatch, MedicineProduct, TreatmentCourse

pytestmark = pytest.mark.django_db


def headers(farm):
    return {"HTTP_X_FARM_ID": str(farm.id)}


def medicine_setup(farm, user, *, stock="20.00", planned_doses=1):
    animal = Animal.objects.create(farm=farm, ear_tag="MED-1", species="sheep")
    product = MedicineProduct.objects.create(
        farm=farm,
        name="Example medicine",
        stock_unit="ml",
        meat_withdrawal_days=7,
        milk_withdrawal_days=3,
    )
    batch = MedicineBatch.objects.create(
        farm=farm,
        product=product,
        batch_number="LOT-1",
        expiry_date=date.today() + timedelta(days=90),
        quantity_on_hand=stock,
    )
    course = TreatmentCourse.objects.create(
        farm=farm,
        animal=animal,
        product=product,
        reason="Infection",
        dosage="2 ml",
        started_on=date.today(),
        planned_doses=planned_doses,
        prescribed_by=user,
    )
    return animal, product, batch, course


def test_administering_dose_deducts_stock_and_completes_course(api_client, farm, user):
    _, _, batch, course = medicine_setup(farm, user)
    administered_at = datetime.now(UTC).replace(microsecond=0)
    response = api_client.post(
        "/api/v1/medicine/administrations/",
        {
            "course": str(course.id),
            "batch": str(batch.id),
            "administered_at": administered_at.isoformat(),
            "quantity_used": "2.00",
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 201
    batch.refresh_from_db()
    course.refresh_from_db()
    assert batch.quantity_on_hand == Decimal("18.00")
    assert course.status == TreatmentCourse.Status.COMPLETED
    assert course.meat_withdrawal_end_date == administered_at.date() + timedelta(days=7)


def test_administration_rejects_insufficient_stock(api_client, farm, user):
    _, _, batch, course = medicine_setup(farm, user, stock="1.00")
    response = api_client.post(
        "/api/v1/medicine/administrations/",
        {
            "course": str(course.id),
            "batch": str(batch.id),
            "administered_at": datetime.now(UTC).isoformat(),
            "quantity_used": "2.00",
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400
    assert DoseAdministration.objects.count() == 0


def test_administration_rejects_expired_batch(api_client, farm, user):
    _, _, batch, course = medicine_setup(farm, user)
    batch.expiry_date = date.today() - timedelta(days=1)
    batch.save()
    response = api_client.post(
        "/api/v1/medicine/administrations/",
        {
            "course": str(course.id),
            "batch": str(batch.id),
            "administered_at": datetime.now(UTC).isoformat(),
            "quantity_used": "1.00",
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400


def test_course_rejects_cross_farm_product(api_client, farm, user):
    animal = Animal.objects.create(farm=farm, ear_tag="MED-2", species="goat")
    other_farm = Farm.objects.create(name="Other", owner=user)
    product = MedicineProduct.objects.create(farm=other_farm, name="Other product")
    response = api_client.post(
        "/api/v1/medicine/courses/",
        {
            "animal": str(animal.id),
            "product": str(product.id),
            "reason": "Test",
            "dosage": "1 ml",
            "started_on": date.today(),
            "planned_doses": 1,
        },
        format="json",
        **headers(farm),
    )
    assert response.status_code == 400


def test_dose_administrations_are_append_only(api_client, farm, user):
    _, _, batch, course = medicine_setup(farm, user)
    administration = DoseAdministration.objects.create(
        farm=farm,
        course=course,
        batch=batch,
        administered_at=datetime.now(UTC),
        quantity_used="1.00",
        administered_by=user,
    )
    response = api_client.patch(
        f"/api/v1/medicine/administrations/{administration.id}/",
        {"quantity_used": "9.00"},
        format="json",
        **headers(farm),
    )
    assert response.status_code == 405
