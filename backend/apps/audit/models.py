from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class AuditEvent(TimeStampedModel):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"

    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, related_name="audit_events")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    resource_type = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=100)
    resource_name = models.CharField(max_length=250)
    animal_id = models.UUIDField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["farm", "created_at"]),
            models.Index(fields=["farm", "resource_type", "created_at"]),
            models.Index(fields=["farm", "animal_id", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Audit events are immutable")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Audit events are immutable")
