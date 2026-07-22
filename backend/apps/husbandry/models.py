from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.animals.models import Animal, Flock
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class HusbandryTask(TimeStampedModel):
    class TaskType(models.TextChoices):
        VACCINATION = "vaccination", "Vaccination"
        PARASITE = "parasite", "Parasite assessment or deworming"
        SHEARING = "shearing", "Shearing"
        HOOF_CARE = "hoof_care", "Hoof care"
        WEIGHING = "weighing", "Weighing"
        HEALTH_CHECK = "health_check", "Health check"
        BREEDING = "breeding", "Breeding"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="husbandry_tasks")
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="husbandry_tasks",
        null=True,
        blank=True,
    )
    flock = models.ForeignKey(
        Flock,
        on_delete=models.CASCADE,
        related_name="husbandry_tasks",
        null=True,
        blank=True,
    )
    task_type = models.CharField(max_length=30, choices=TaskType.choices)
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    recurrence_days = models.PositiveIntegerField(null=True, blank=True)
    reminder_days_before = models.PositiveSmallIntegerField(default=1)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="completed_husbandry_tasks",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["due_date", "created_at"]
        indexes = [models.Index(fields=["farm", "status", "due_date"])]

    def clean(self):
        if self.animal_id and self.animal.farm_id != self.farm_id:
            raise ValidationError({"animal": "Animal must belong to the task farm"})
        if self.flock_id and self.flock.farm_id != self.farm_id:
            raise ValidationError({"flock": "Flock must belong to the task farm"})
