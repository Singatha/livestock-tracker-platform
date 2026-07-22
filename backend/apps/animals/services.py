from django.db import transaction
from django.utils import timezone

from .models import Animal, AnimalLifecycleEvent, Flock


@transaction.atomic
def register_lifecycle_event(*, animal: Animal, recorded_by) -> AnimalLifecycleEvent:
    return AnimalLifecycleEvent.objects.create(
        animal=animal,
        farm=animal.farm,
        event_type=AnimalLifecycleEvent.EventType.REGISTERED,
        effective_date=timezone.localdate(),
        to_status=animal.status,
        to_flock=animal.flock,
        reason="Animal registered",
        recorded_by=recorded_by,
    )


@transaction.atomic
def change_animal_status(*, animal: Animal, status: str, effective_date, reason: str, recorded_by):
    animal = Animal.objects.select_for_update().select_related("farm").get(pk=animal.pk)
    if animal.status == Animal.Status.DECEASED:
        raise ValueError("A deceased animal cannot transition to another status")
    if animal.status == status:
        raise ValueError("Animal already has this status")
    previous = animal.status
    animal.status = status
    if status != Animal.Status.ACTIVE:
        animal.needs_attention = False
    animal.save(update_fields=["status", "needs_attention", "updated_at"])
    AnimalLifecycleEvent.objects.create(
        animal=animal,
        farm=animal.farm,
        event_type=AnimalLifecycleEvent.EventType.STATUS_CHANGED,
        effective_date=effective_date,
        from_status=previous,
        to_status=status,
        reason=reason,
        recorded_by=recorded_by,
    )
    return animal


@transaction.atomic
def transfer_animal(
    *, animal: Animal, flock: Flock | None, effective_date, reason: str, recorded_by
):
    animal = Animal.objects.select_for_update().select_related("farm").get(pk=animal.pk)
    if animal.status != Animal.Status.ACTIVE:
        raise ValueError("Only active animals can be transferred")
    if animal.flock_id == (flock.id if flock else None):
        raise ValueError("Animal already belongs to this flock")
    previous = animal.flock
    animal.flock = flock
    animal.save(update_fields=["flock", "updated_at"])
    AnimalLifecycleEvent.objects.create(
        animal=animal,
        farm=animal.farm,
        event_type=AnimalLifecycleEvent.EventType.FLOCK_TRANSFERRED,
        effective_date=effective_date,
        from_flock=previous,
        to_flock=flock,
        reason=reason,
        recorded_by=recorded_by,
    )
    return animal
