from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.animals.models import Animal, Flock
from apps.attachments.models import Attachment
from apps.growth.models import WeightMeasurement
from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask
from apps.medicine.models import (
    DoseAdministration,
    MedicineBatch,
    MedicineProduct,
    TreatmentCourse,
)
from apps.nutrition.models import Feed, FeedingPlan, FeedingPlanItem
from apps.reproduction.models import BirthRecord, BreedingRecord

from .context import audit_context
from .models import AuditEvent

TRACKED_MODELS = (
    Attachment,
    Flock,
    Animal,
    HealthObservation,
    Treatment,
    HusbandryTask,
    WeightMeasurement,
    BreedingRecord,
    BirthRecord,
    Feed,
    FeedingPlan,
    FeedingPlanItem,
    MedicineProduct,
    MedicineBatch,
    TreatmentCourse,
    DoseAdministration,
)
IGNORED_FIELDS = {"id", "created_at", "updated_at", "farm"}


def _value(value):
    if hasattr(value, "name") and not isinstance(value, str):
        return value.name
    if isinstance(value, (date, datetime, Decimal, UUID)):
        return str(value)
    return value


def _snapshot(instance):
    return {
        field.name: _value(getattr(instance, field.attname))
        for field in instance._meta.concrete_fields
        if field.name not in IGNORED_FIELDS
    }


def _farm_id(instance):
    if hasattr(instance, "farm_id"):
        return instance.farm_id
    if isinstance(instance, FeedingPlanItem):
        return instance.plan.farm_id
    return None


def _animal_id(instance):
    if isinstance(instance, Animal):
        return instance.id
    return getattr(instance, "animal_id", None)


def _resource_name(instance):
    for field in ("ear_tag", "name", "title", "summary", "batch_number", "reason"):
        if value := getattr(instance, field, None):
            return str(value)
    return str(instance)


def _can_record(instance):
    actor, selected_farm_id = audit_context()
    farm_id = _farm_id(instance)
    return actor is not None and farm_id is not None and str(farm_id) == str(selected_farm_id)


@receiver(pre_save)
def capture_previous_state(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS or instance._state.adding or not _can_record(instance):
        return
    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    instance._audit_previous = _snapshot(previous)


@receiver(post_save)
def record_save(sender, instance, created, **kwargs):
    if sender not in TRACKED_MODELS or not _can_record(instance):
        return
    current = _snapshot(instance)
    if created:
        changes = current
        action = AuditEvent.Action.CREATED
    else:
        previous = getattr(instance, "_audit_previous", {})
        changes = {
            key: {"from": previous.get(key), "to": value}
            for key, value in current.items()
            if previous.get(key) != value
        }
        if not changes:
            return
        action = AuditEvent.Action.UPDATED
    actor, _ = audit_context()
    AuditEvent.objects.create(
        farm_id=_farm_id(instance),
        actor=actor,
        action=action,
        resource_type=sender._meta.verbose_name.title(),
        resource_id=str(instance.pk),
        resource_name=_resource_name(instance),
        animal_id=_animal_id(instance),
        changes=changes,
    )


@receiver(post_delete)
def record_delete(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS or not _can_record(instance):
        return
    actor, _ = audit_context()
    AuditEvent.objects.create(
        farm_id=_farm_id(instance),
        actor=actor,
        action=AuditEvent.Action.DELETED,
        resource_type=sender._meta.verbose_name.title(),
        resource_id=str(instance.pk),
        resource_name=_resource_name(instance),
        animal_id=_animal_id(instance),
        changes=_snapshot(instance),
    )
