from rest_framework import serializers

from .models import Animal, Flock


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
