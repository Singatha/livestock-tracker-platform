from django.conf import settings
from django.db import models

from apps.animals.models import Animal
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class MedicineProduct(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="medicine_products")
    name = models.CharField(max_length=200)
    active_ingredient = models.CharField(max_length=200, blank=True)
    concentration = models.CharField(max_length=100, blank=True)
    stock_unit = models.CharField(max_length=20, default="ml")
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meat_withdrawal_days = models.PositiveSmallIntegerField(default=0)
    milk_withdrawal_days = models.PositiveSmallIntegerField(default=0)
    instructions = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["farm", "name"], name="unique_farm_medicine")
        ]


class MedicineBatch(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="medicine_batches")
    product = models.ForeignKey(MedicineProduct, on_delete=models.PROTECT, related_name="batches")
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity_on_hand = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["expiry_date", "batch_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "batch_number"], name="unique_medicine_product_batch"
            )
        ]
        indexes = [models.Index(fields=["farm", "expiry_date"])]


class TreatmentCourse(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="treatment_courses")
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name="treatment_courses")
    product = models.ForeignKey(
        MedicineProduct, on_delete=models.PROTECT, related_name="treatment_courses"
    )
    reason = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    route = models.CharField(max_length=50, blank=True)
    started_on = models.DateField()
    planned_doses = models.PositiveSmallIntegerField(default=1)
    frequency_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    meat_withdrawal_end_date = models.DateField(null=True, blank=True)
    milk_withdrawal_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prescribed_treatment_courses",
    )

    class Meta:
        ordering = ["-started_on", "-created_at"]
        indexes = [models.Index(fields=["farm", "status", "started_on"])]


class DoseAdministration(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="dose_administrations")
    course = models.ForeignKey(
        TreatmentCourse, on_delete=models.PROTECT, related_name="administrations"
    )
    batch = models.ForeignKey(
        MedicineBatch, on_delete=models.PROTECT, related_name="administrations"
    )
    administered_at = models.DateTimeField()
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="administered_medicine_doses",
    )

    class Meta:
        ordering = ["-administered_at", "-created_at"]
        indexes = [models.Index(fields=["farm", "administered_at"])]
