from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.farms.models import Farm
from apps.husbandry.models import HusbandryTask


class Notification(TimeStampedModel):
    class Kind(models.TextChoices):
        TASK_DUE = "task_due", "Task due soon"
        TASK_OVERDUE = "task_overdue", "Task overdue"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    task = models.ForeignKey(HusbandryTask, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=30, choices=Kind.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, default="/tasks")
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "task", "kind"], name="unique_task_notification"
            )
        ]
        indexes = [models.Index(fields=["farm", "recipient", "read_at"])]
