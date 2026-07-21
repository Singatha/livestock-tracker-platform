from rest_framework import serializers

from .models import HusbandryTask


class HusbandryTaskSerializer(serializers.ModelSerializer):
    completed_by_name = serializers.CharField(source="completed_by.get_full_name", read_only=True)

    class Meta:
        model = HusbandryTask
        fields = [
            "id",
            "farm",
            "animal",
            "flock",
            "task_type",
            "title",
            "due_date",
            "status",
            "recurrence_days",
            "notes",
            "completed_at",
            "completion_notes",
            "completed_by",
            "completed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "status",
            "completed_at",
            "completion_notes",
            "completed_by",
            "completed_by_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        farm = self.context["farm"]
        animal = attrs.get("animal", getattr(self.instance, "animal", None))
        flock = attrs.get("flock", getattr(self.instance, "flock", None))
        if animal is not None and animal.farm_id != farm.id:
            raise serializers.ValidationError(
                {"animal": "Animal does not belong to the selected farm"}
            )
        if flock is not None and flock.farm_id != farm.id:
            raise serializers.ValidationError(
                {"flock": "Flock does not belong to the selected farm"}
            )
        return attrs


class CompleteTaskSerializer(serializers.Serializer):
    completion_notes = serializers.CharField(required=False, allow_blank=True, default="")
