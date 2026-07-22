from django.conf import settings
from django.db import models

from apps.animals.models import Animal
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class WeightMeasurement(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="weight_measurements")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="weight_measurements")
    measured_on = models.DateField()
    weight_kg = models.DecimalField(max_digits=7, decimal_places=2)
    body_condition_score = models.DecimalField(
        max_digits=2, decimal_places=1, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_weight_measurements",
    )

    class Meta:
        ordering = ["-measured_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["animal", "measured_on"], name="unique_animal_weight_per_day"
            )
        ]
        indexes = [models.Index(fields=["farm", "measured_on"])]
