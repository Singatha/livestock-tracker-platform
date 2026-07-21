from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Farm(TimeStampedModel):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_farms"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class FarmMembership(TimeStampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        WORKER = "worker", "Worker"
        VIEWER = "viewer", "Viewer"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="farm_memberships"
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["farm", "user"], name="unique_farm_member")]

    def __str__(self) -> str:
        return f"{self.user} at {self.farm}"
