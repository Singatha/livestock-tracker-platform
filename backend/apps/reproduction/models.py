from django.conf import settings
from django.db import models

from apps.animals.models import Animal
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class BreedingRecord(TimeStampedModel):
    class Method(models.TextChoices):
        NATURAL = "natural", "Natural service"
        ARTIFICIAL = "artificial", "Artificial insemination"
        UNKNOWN = "unknown", "Unknown"

    class Status(models.TextChoices):
        EXPOSED = "exposed", "Exposed"
        CONFIRMED = "confirmed", "Pregnancy confirmed"
        NOT_PREGNANT = "not_pregnant", "Not pregnant"
        COMPLETED = "completed", "Birth recorded"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="breeding_records")
    dam = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name="breeding_as_dam")
    sire = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="breeding_as_sire",
        null=True,
        blank=True,
    )
    breeding_date = models.DateField()
    expected_birth_date = models.DateField()
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.NATURAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EXPOSED)
    pregnancy_checked_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_breeding_records",
    )

    class Meta:
        ordering = ["expected_birth_date", "created_at"]
        indexes = [models.Index(fields=["farm", "status", "expected_birth_date"])]


class BirthRecord(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="birth_records")
    breeding = models.OneToOneField(
        BreedingRecord, on_delete=models.PROTECT, related_name="birth_record"
    )
    dam = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name="births_as_dam")
    birth_date = models.DateField()
    total_born = models.PositiveSmallIntegerField()
    born_alive = models.PositiveSmallIntegerField()
    stillborn = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_birth_records",
    )

    class Meta:
        ordering = ["-birth_date", "-created_at"]
        indexes = [models.Index(fields=["farm", "birth_date"])]
