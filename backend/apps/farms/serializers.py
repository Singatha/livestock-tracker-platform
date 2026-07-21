from django.db import transaction
from rest_framework import serializers

from .models import Farm, FarmMembership


class FarmSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Farm
        fields = ["id", "name", "role", "created_at", "updated_at"]
        read_only_fields = ["id", "role", "created_at", "updated_at"]

    def get_role(self, farm: Farm) -> str | None:
        membership = next(
            (
                item
                for item in farm.memberships.all()
                if item.user_id == self.context["request"].user.id
            ),
            None,
        )
        return membership.role if membership else None

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        farm = Farm.objects.create(owner=user, **validated_data)
        FarmMembership.objects.create(farm=farm, user=user, role=FarmMembership.Role.OWNER)
        return farm
