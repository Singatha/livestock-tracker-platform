from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.animals.models import Animal
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class HealthObservation(TimeStampedModel):
    class Category(models.TextChoices):
        GENERAL = "general", "General health"
        INJURY = "injury", "Injury"
        ILLNESS = "illness", "Illness"
        PARASITE = "parasite", "Parasite concern"
        REPRODUCTIVE = "reproductive", "Reproductive"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="health_observations")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="health_observations")
    observed_at = models.DateTimeField(default=timezone.now)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.LOW)
    summary = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_health_observations",
    )

    class Meta:
        ordering = ["-observed_at"]
        indexes = [models.Index(fields=["farm", "is_resolved", "severity"])]


class Treatment(TimeStampedModel):
    class Route(models.TextChoices):
        ORAL = "oral", "Oral"
        INJECTION = "injection", "Injection"
        TOPICAL = "topical", "Topical"
        OTHER = "other", "Other"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="treatments")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="treatments")
    observation = models.ForeignKey(
        HealthObservation,
        on_delete=models.SET_NULL,
        related_name="treatments",
        null=True,
        blank=True,
    )
    administered_at = models.DateTimeField(default=timezone.now)
    product = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=20, choices=Route.choices, default=Route.OTHER)
    reason = models.CharField(max_length=200, blank=True)
    withdrawal_end_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_treatments",
    )

    class Meta:
        ordering = ["-administered_at"]
        indexes = [models.Index(fields=["farm", "administered_at"])]
