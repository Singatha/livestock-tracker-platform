from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class ImportJob(TimeStampedModel):
    class Kind(models.TextChoices):
        FLOCKS = "flocks", "Flocks"
        ANIMALS = "animals", "Animals"
        WEIGHTS = "weights", "Weights"
        MEDICINE_BATCHES = "medicine_batches", "Medicine batches"

    class Mode(models.TextChoices):
        ALL_OR_NOTHING = "all_or_nothing", "All or nothing"
        PARTIAL = "partial", "Import valid rows"

    class Status(models.TextChoices):
        PREVIEWED = "previewed", "Previewed"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="import_jobs")
    kind = models.CharField(max_length=30, choices=Kind.choices)
    mode = models.CharField(max_length=20, choices=Mode.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PREVIEWED)
    original_filename = models.CharField(max_length=255)
    rows = models.JSONField(default=list)
    errors = models.JSONField(default=list)
    rows_total = models.PositiveIntegerField(default=0)
    rows_succeeded = models.PositiveIntegerField(default=0)
    rows_failed = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_import_jobs",
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["farm", "status", "created_at"])]
