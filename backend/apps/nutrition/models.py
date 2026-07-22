from django.core.exceptions import ValidationError
from django.db import models

from apps.animals.models import Flock
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


class Feed(TimeStampedModel):
    class Category(models.TextChoices):
        FORAGE = "forage", "Forage"
        CONCENTRATE = "concentrate", "Concentrate"
        MINERAL = "mineral", "Mineral"
        SUPPLEMENT = "supplement", "Supplement"
        OTHER = "other", "Other"

    class Suitability(models.TextChoices):
        SHEEP = "sheep", "Sheep"
        GOAT = "goat", "Goat"
        BOTH = "both", "Sheep and goats"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="feeds")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    suitability = models.CharField(
        max_length=10, choices=Suitability.choices, default=Suitability.BOTH
    )
    unit = models.CharField(max_length=20, default="kg")
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["farm", "name"], name="unique_farm_feed")]

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level


class FeedingPlan(TimeStampedModel):
    class LifeStage(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        GROWING = "growing", "Growing"
        GESTATION = "gestation", "Gestation"
        LACTATION = "lactation", "Lactation"
        FINISHING = "finishing", "Finishing"
        CUSTOM = "custom", "Custom"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="feeding_plans")
    flock = models.ForeignKey(Flock, on_delete=models.CASCADE, related_name="feeding_plans")
    name = models.CharField(max_length=200)
    life_stage = models.CharField(max_length=20, choices=LifeStage.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-is_active", "name"]

    def clean(self):
        if self.flock_id and self.flock.farm_id != self.farm_id:
            raise ValidationError({"flock": "Flock must belong to the plan farm"})
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot precede start date"})


class FeedingPlanItem(TimeStampedModel):
    plan = models.ForeignKey(FeedingPlan, on_delete=models.CASCADE, related_name="items")
    feed = models.ForeignKey(Feed, on_delete=models.PROTECT, related_name="plan_items")
    quantity_per_animal = models.DecimalField(max_digits=8, decimal_places=3)
    feeding_time = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["plan", "feed"], name="unique_plan_feed")]

    def clean(self):
        if self.feed_id and self.plan_id and self.feed.farm_id != self.plan.farm_id:
            raise ValidationError({"feed": "Feed must belong to the plan farm"})
