from rest_framework import serializers

from apps.animals.models import Animal

from .models import HealthObservation, Treatment


class FarmRelationValidationMixin:
    def validate_animal(self, animal: Animal) -> Animal:
        if animal.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Animal does not belong to the selected farm")
        return animal


class HealthObservationSerializer(FarmRelationValidationMixin, serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = HealthObservation
        fields = [
            "id",
            "farm",
            "animal",
            "observed_at",
            "category",
            "severity",
            "summary",
            "notes",
            "is_resolved",
            "recorded_by",
            "recorded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "recorded_by",
            "recorded_by_name",
            "created_at",
            "updated_at",
        ]


class TreatmentSerializer(FarmRelationValidationMixin, serializers.ModelSerializer):
    administered_by_name = serializers.CharField(
        source="administered_by.get_full_name", read_only=True
    )

    class Meta:
        model = Treatment
        fields = [
            "id",
            "farm",
            "animal",
            "observation",
            "administered_at",
            "product",
            "dosage",
            "route",
            "reason",
            "withdrawal_end_date",
            "follow_up_date",
            "notes",
            "administered_by",
            "administered_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "administered_by",
            "administered_by_name",
            "created_at",
            "updated_at",
        ]

    def validate_observation(self, observation: HealthObservation | None):
        if observation is not None and observation.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Observation does not belong to the selected farm")
        return observation

    def validate(self, attrs):
        observation = attrs.get("observation", getattr(self.instance, "observation", None))
        animal = attrs.get("animal", getattr(self.instance, "animal", None))
        if observation is not None and animal is not None and observation.animal_id != animal.id:
            raise serializers.ValidationError(
                {"observation": "Observation must belong to the selected animal"}
            )
        return attrs
