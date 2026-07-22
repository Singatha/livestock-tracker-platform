from django.db import transaction
from rest_framework import serializers

from .models import Feed, FeedingPlan, FeedingPlanItem


class FeedSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Feed
        fields = [
            "id",
            "farm",
            "name",
            "category",
            "suitability",
            "unit",
            "quantity_on_hand",
            "reorder_level",
            "unit_cost",
            "notes",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "farm", "is_low_stock", "created_at", "updated_at"]


class FeedingPlanItemSerializer(serializers.ModelSerializer):
    feed_name = serializers.CharField(source="feed.name", read_only=True)
    unit = serializers.CharField(source="feed.unit", read_only=True)

    class Meta:
        model = FeedingPlanItem
        fields = ["id", "feed", "feed_name", "unit", "quantity_per_animal", "feeding_time"]


class FeedingPlanSerializer(serializers.ModelSerializer):
    items = FeedingPlanItemSerializer(many=True)
    flock_name = serializers.CharField(source="flock.name", read_only=True)
    compatibility_warnings = serializers.SerializerMethodField()

    class Meta:
        model = FeedingPlan
        fields = [
            "id",
            "farm",
            "flock",
            "flock_name",
            "name",
            "life_stage",
            "start_date",
            "end_date",
            "is_active",
            "notes",
            "items",
            "compatibility_warnings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "flock_name",
            "compatibility_warnings",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        farm = self.context["farm"]
        flock = attrs.get("flock", getattr(self.instance, "flock", None))
        if flock and flock.farm_id != farm.id:
            raise serializers.ValidationError(
                {"flock": "Flock does not belong to the selected farm"}
            )
        if attrs.get("end_date") and attrs["end_date"] < attrs.get(
            "start_date", self.instance.start_date if self.instance else attrs["end_date"]
        ):
            raise serializers.ValidationError({"end_date": "End date cannot precede start date"})
        items = attrs.get("items", [])
        feed_ids = [item["feed"].id for item in items]
        if len(feed_ids) != len(set(feed_ids)):
            raise serializers.ValidationError({"items": "Each feed may appear only once"})
        if any(item["feed"].farm_id != farm.id for item in items):
            raise serializers.ValidationError(
                {"items": "All feeds must belong to the selected farm"}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items", [])
        plan = FeedingPlan.objects.create(**validated_data)
        self._save_items(plan, items)
        return plan

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        if items is not None:
            instance.items.all().delete()
            self._save_items(instance, items)
        return instance

    def _save_items(self, plan, items):
        for item in items:
            FeedingPlanItem.objects.create(plan=plan, **item)

    def get_compatibility_warnings(self, obj) -> list[str]:
        species = set(obj.flock.animals.filter(status="active").values_list("species", flat=True))
        warnings = []
        for item in obj.items.all():
            if item.feed.suitability != Feed.Suitability.BOTH and any(
                value != item.feed.suitability for value in species
            ):
                suitability = item.feed.get_suitability_display().lower()
                warnings.append(f"{item.feed.name} is marked for {suitability} only.")
        return warnings
