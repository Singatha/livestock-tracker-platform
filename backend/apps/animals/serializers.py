from rest_framework import serializers

from .models import Animal, AnimalLifecycleEvent, Flock


class FlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flock
        fields = ["id", "farm", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "farm", "created_at", "updated_at"]

    def validate_name(self, name: str) -> str:
        farm = self.context["farm"]
        queryset = Flock.objects.filter(farm=farm, name__iexact=name)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A flock with this name already exists")
        return name


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = [
            "id",
            "farm",
            "flock",
            "ear_tag",
            "name",
            "species",
            "breed",
            "sex",
            "date_of_birth",
            "status",
            "needs_attention",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "farm", "created_at", "updated_at"]

    def validate_ear_tag(self, ear_tag: str) -> str:
        farm = self.context["farm"]
        queryset = Animal.objects.filter(farm=farm, ear_tag__iexact=ear_tag)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("This ear tag is already registered")
        return ear_tag

    def validate_flock(self, flock: Flock | None) -> Flock | None:
        farm = self.context["farm"]
        if flock is not None and flock.farm_id != farm.id:
            raise serializers.ValidationError("Flock does not belong to the selected farm")
        return flock

    def validate(self, attrs):
        if self.instance is not None:
            if "status" in attrs and attrs["status"] != self.instance.status:
                raise serializers.ValidationError(
                    {"status": "Use the lifecycle status action to change status"}
                )
            if "flock" in attrs and attrs["flock"] != self.instance.flock:
                raise serializers.ValidationError(
                    {"flock": "Use the flock transfer action to move an animal"}
                )
        return attrs


class ChangeAnimalStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Animal.Status.choices)
    effective_date = serializers.DateField()
    reason = serializers.CharField(max_length=250)


class TransferAnimalSerializer(serializers.Serializer):
    flock = serializers.PrimaryKeyRelatedField(
        queryset=Flock.objects.all(), allow_null=True, required=True
    )
    effective_date = serializers.DateField()
    reason = serializers.CharField(max_length=250, required=False, allow_blank=True)

    def validate_flock(self, flock):
        if flock is not None and flock.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Flock does not belong to the selected farm")
        return flock


class AnimalLifecycleEventSerializer(serializers.ModelSerializer):
    from_flock_name = serializers.CharField(source="from_flock.name", read_only=True)
    to_flock_name = serializers.CharField(source="to_flock.name", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = AnimalLifecycleEvent
        fields = [
            "id",
            "event_type",
            "effective_date",
            "from_status",
            "to_status",
            "from_flock",
            "from_flock_name",
            "to_flock",
            "to_flock_name",
            "reason",
            "recorded_by_name",
            "created_at",
        ]


class TimelineEventSerializer(serializers.Serializer):
    id = serializers.CharField()
    kind = serializers.ChoiceField(choices=["observation", "treatment", "task", "lifecycle"])
    date = serializers.CharField()
    title = serializers.CharField()
    details = serializers.CharField(allow_blank=True)
    status = serializers.CharField()
