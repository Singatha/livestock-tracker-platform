from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class Flock(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="flocks")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["farm", "name"], name="unique_flock_name_per_farm")
        ]

    def __str__(self) -> str:
        return self.name


class Animal(TimeStampedModel):
    class Species(models.TextChoices):
        SHEEP = "sheep", "Sheep"
        GOAT = "goat", "Goat"

    class Sex(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        UNKNOWN = "unknown", "Unknown"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SOLD = "sold", "Sold"
        DECEASED = "deceased", "Deceased"
        MISSING = "missing", "Missing"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="animals")
    flock = models.ForeignKey(
        Flock, on_delete=models.SET_NULL, related_name="animals", null=True, blank=True
    )
    ear_tag = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True)
    species = models.CharField(max_length=20, choices=Species.choices)
    breed = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=20, choices=Sex.choices, default=Sex.UNKNOWN)
    date_of_birth = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    needs_attention = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["ear_tag"]
        constraints = [
            models.UniqueConstraint(fields=["farm", "ear_tag"], name="unique_ear_tag_per_farm")
        ]
        indexes = [
            models.Index(fields=["farm", "status"]),
            models.Index(fields=["farm", "species"]),
        ]

    def __str__(self) -> str:
        return self.ear_tag


class AnimalLifecycleEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        REGISTERED = "registered", "Registered"
        STATUS_CHANGED = "status_changed", "Status changed"
        FLOCK_TRANSFERRED = "flock_transferred", "Flock transferred"

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="lifecycle_events")
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="animal_lifecycle_events")
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    effective_date = models.DateField()
    from_status = models.CharField(max_length=20, choices=Animal.Status.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=Animal.Status.choices, blank=True)
    from_flock = models.ForeignKey(
        Flock,
        on_delete=models.SET_NULL,
        related_name="lifecycle_events_from",
        null=True,
        blank=True,
    )
    to_flock = models.ForeignKey(
        Flock,
        on_delete=models.SET_NULL,
        related_name="lifecycle_events_to",
        null=True,
        blank=True,
    )
    reason = models.CharField(max_length=250, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_animal_lifecycle_events",
    )

    class Meta:
        ordering = ["-effective_date", "-created_at"]
        indexes = [
            models.Index(
                fields=["farm", "event_type", "effective_date"],
                name="animals_ani_farm_id_6c53ca_idx",
            )
        ]
