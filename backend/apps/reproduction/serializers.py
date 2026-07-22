from datetime import timedelta

from django.db import transaction
from rest_framework import serializers

from apps.animals.models import Animal

from .models import BirthRecord, BreedingRecord


class BreedingRecordSerializer(serializers.ModelSerializer):
    dam_name = serializers.CharField(source="dam.ear_tag", read_only=True)
    sire_name = serializers.CharField(source="sire.ear_tag", read_only=True)

    class Meta:
        model = BreedingRecord
        fields = [
            "id",
            "farm",
            "dam",
            "dam_name",
            "sire",
            "sire_name",
            "breeding_date",
            "expected_birth_date",
            "method",
            "status",
            "pregnancy_checked_on",
            "notes",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "farm", "recorded_by", "created_at", "updated_at"]
        extra_kwargs = {"expected_birth_date": {"required": False}}

    def validate(self, attrs):
        farm = self.context["farm"]
        dam = attrs.get("dam", getattr(self.instance, "dam", None))
        sire = attrs.get("sire", getattr(self.instance, "sire", None))
        status = attrs.get(
            "status", getattr(self.instance, "status", BreedingRecord.Status.EXPOSED)
        )
        checked_on = attrs.get(
            "pregnancy_checked_on", getattr(self.instance, "pregnancy_checked_on", None)
        )
        if dam is not None and (dam.farm_id != farm.id or dam.sex != Animal.Sex.FEMALE):
            raise serializers.ValidationError({"dam": "Dam must be a female from this farm"})
        if sire is not None:
            if sire.farm_id != farm.id or sire.sex != Animal.Sex.MALE:
                raise serializers.ValidationError({"sire": "Sire must be a male from this farm"})
            if dam is not None and sire.species != dam.species:
                raise serializers.ValidationError({"sire": "Sire and dam must be the same species"})
        if dam is not None and dam.status != Animal.Status.ACTIVE:
            raise serializers.ValidationError({"dam": "Dam must be active"})
        if (
            status in {BreedingRecord.Status.CONFIRMED, BreedingRecord.Status.NOT_PREGNANT}
            and not checked_on
        ):
            raise serializers.ValidationError(
                {"pregnancy_checked_on": "A check date is required for this status"}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        if not validated_data.get("expected_birth_date"):
            gestation_days = 147 if validated_data["dam"].species == Animal.Species.SHEEP else 150
            validated_data["expected_birth_date"] = validated_data["breeding_date"] + timedelta(
                days=gestation_days
            )
        return super().create(validated_data)


class BirthRecordSerializer(serializers.ModelSerializer):
    dam_name = serializers.CharField(source="dam.ear_tag", read_only=True)

    class Meta:
        model = BirthRecord
        fields = [
            "id",
            "farm",
            "breeding",
            "dam",
            "dam_name",
            "birth_date",
            "total_born",
            "born_alive",
            "stillborn",
            "notes",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "dam",
            "recorded_by",
            "created_at",
            "updated_at",
        ]

    def validate_breeding(self, breeding):
        if breeding.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Breeding record does not belong to this farm")
        if breeding.status not in {
            BreedingRecord.Status.EXPOSED,
            BreedingRecord.Status.CONFIRMED,
        }:
            raise serializers.ValidationError("Births can only be recorded for an open breeding")
        if hasattr(breeding, "birth_record") and (
            self.instance is None or breeding.birth_record != self.instance
        ):
            raise serializers.ValidationError("A birth is already recorded for this breeding")
        return breeding

    def validate(self, attrs):
        total = attrs.get("total_born", getattr(self.instance, "total_born", 0))
        alive = attrs.get("born_alive", getattr(self.instance, "born_alive", 0))
        stillborn = attrs.get("stillborn", getattr(self.instance, "stillborn", 0))
        if alive + stillborn != total:
            raise serializers.ValidationError(
                "Born alive and stillborn counts must equal the total born"
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        breeding = validated_data["breeding"]
        validated_data["dam"] = breeding.dam
        record = super().create(validated_data)
        breeding.status = BreedingRecord.Status.COMPLETED
        breeding.save(update_fields=["status", "updated_at"])
        return record
