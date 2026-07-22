import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

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


class FarmInvitation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REVOKED = "revoked", "Revoked"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=FarmMembership.Role.choices)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_farm_invitations",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="accepted_farm_invitations",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["farm", "status", "email"])]

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()


class FarmMembershipAudit(TimeStampedModel):
    class EventType(models.TextChoices):
        INVITED = "invited", "Invited"
        ACCEPTED = "accepted", "Invitation accepted"
        ROLE_CHANGED = "role_changed", "Role changed"
        DEACTIVATED = "deactivated", "Deactivated"
        REACTIVATED = "reactivated", "Reactivated"
        INVITATION_REVOKED = "invitation_revoked", "Invitation revoked"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="membership_audits")
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    subject_email = models.EmailField()
    from_role = models.CharField(max_length=20, choices=FarmMembership.Role.choices, blank=True)
    to_role = models.CharField(max_length=20, choices=FarmMembership.Role.choices, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="farm_membership_actions",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["farm", "event_type", "created_at"])]
