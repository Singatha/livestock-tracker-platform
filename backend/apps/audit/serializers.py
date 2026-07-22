from rest_framework import serializers

from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "action",
            "resource_type",
            "resource_id",
            "resource_name",
            "animal_id",
            "changes",
            "actor_name",
            "created_at",
        ]

    def get_actor_name(self, obj):
        if not obj.actor:
            return "Former user"
        return obj.actor.get_full_name() or obj.actor.email or obj.actor.username
