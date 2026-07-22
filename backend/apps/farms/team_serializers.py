from rest_framework import serializers

from .models import FarmInvitation, FarmMembership, FarmMembershipAudit


class FarmMembershipSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = FarmMembership
        fields = ["id", "user", "email", "name", "role", "is_active", "created_at"]
        read_only_fields = fields

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class FarmInvitationSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = FarmInvitation
        fields = [
            "id",
            "email",
            "role",
            "token",
            "status",
            "expires_at",
            "is_expired",
            "created_at",
        ]
        read_only_fields = ["id", "token", "status", "expires_at", "is_expired", "created_at"]


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=FarmMembership.Role.choices)


class UpdateMembershipSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=FarmMembership.Role.choices, required=False)
    is_active = serializers.BooleanField(required=False)


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class FarmMembershipAuditSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = FarmMembershipAudit
        fields = [
            "id",
            "event_type",
            "subject_email",
            "from_role",
            "to_role",
            "actor_name",
            "created_at",
        ]

    def get_actor_name(self, obj):
        return obj.actor.get_full_name() or obj.actor.username if obj.actor else "System"
