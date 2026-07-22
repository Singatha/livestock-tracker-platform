from rest_framework import serializers

from apps.animals.models import Animal

from .models import WeightMeasurement


class WeightMeasurementSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source="animal.ear_tag", read_only=True)

    class Meta:
        model = WeightMeasurement
        fields = [
            "id",
            "farm",
            "animal",
            "animal_ear_tag",
            "measured_on",
            "weight_kg",
            "body_condition_score",
            "notes",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "farm", "recorded_by", "created_at", "updated_at"]

    def validate_animal(self, animal: Animal) -> Animal:
        if animal.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Animal does not belong to the selected farm")
        return animal

    def validate_weight_kg(self, weight):
        if weight <= 0:
            raise serializers.ValidationError("Weight must be greater than zero")
        return weight

    def validate_body_condition_score(self, score):
        if score is not None and not 1 <= score <= 5:
            raise serializers.ValidationError("Body condition score must be between 1 and 5")
        return score


class AnimalGrowthSummarySerializer(serializers.Serializer):
    animal = serializers.UUIDField()
    ear_tag = serializers.CharField()
    name = serializers.CharField(allow_blank=True)
    flock_name = serializers.CharField(allow_null=True)
    latest_weight_kg = serializers.DecimalField(max_digits=7, decimal_places=2)
    latest_measured_on = serializers.DateField()
    previous_weight_kg = serializers.DecimalField(max_digits=7, decimal_places=2, allow_null=True)
    change_kg = serializers.DecimalField(max_digits=8, decimal_places=2, allow_null=True)
    average_daily_gain_kg = serializers.DecimalField(
        max_digits=8, decimal_places=3, allow_null=True
    )
