from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask
from apps.reproduction.models import BirthRecord, BreedingRecord

from .models import Animal, AnimalLifecycleEvent


def animal_timeline(*, animal: Animal) -> list[dict]:
    events = []
    for observation in HealthObservation.objects.filter(animal=animal).select_related(
        "recorded_by"
    ):
        events.append(
            {
                "id": str(observation.id),
                "kind": "observation",
                "date": observation.observed_at.isoformat(),
                "title": observation.summary,
                "details": observation.notes,
                "status": "resolved" if observation.is_resolved else observation.severity,
            }
        )
    for treatment in Treatment.objects.filter(animal=animal).select_related("administered_by"):
        events.append(
            {
                "id": str(treatment.id),
                "kind": "treatment",
                "date": treatment.administered_at.isoformat(),
                "title": treatment.product,
                "details": treatment.reason or treatment.notes,
                "status": "recorded",
            }
        )
    for task in HusbandryTask.objects.filter(animal=animal):
        events.append(
            {
                "id": str(task.id),
                "kind": "task",
                "date": task.due_date.isoformat(),
                "title": task.title,
                "details": task.notes,
                "status": task.status,
            }
        )
    for lifecycle in AnimalLifecycleEvent.objects.filter(animal=animal).select_related(
        "from_flock", "to_flock"
    ):
        if lifecycle.event_type == AnimalLifecycleEvent.EventType.STATUS_CHANGED:
            details = f"{lifecycle.from_status} to {lifecycle.to_status}"
        elif lifecycle.event_type == AnimalLifecycleEvent.EventType.FLOCK_TRANSFERRED:
            details = (
                f"{lifecycle.from_flock.name if lifecycle.from_flock else 'No flock'} to "
                f"{lifecycle.to_flock.name if lifecycle.to_flock else 'No flock'}"
            )
        else:
            details = lifecycle.reason
        events.append(
            {
                "id": str(lifecycle.id),
                "kind": "lifecycle",
                "date": lifecycle.effective_date.isoformat(),
                "title": lifecycle.get_event_type_display(),
                "details": details,
                "status": lifecycle.to_status or "recorded",
            }
        )
    for breeding in BreedingRecord.objects.filter(dam=animal):
        events.append(
            {
                "id": str(breeding.id),
                "kind": "reproduction",
                "date": breeding.breeding_date.isoformat(),
                "title": "Breeding recorded",
                "details": f"Expected birth {breeding.expected_birth_date.isoformat()}",
                "status": breeding.status,
            }
        )
    for birth in BirthRecord.objects.filter(dam=animal):
        events.append(
            {
                "id": str(birth.id),
                "kind": "reproduction",
                "date": birth.birth_date.isoformat(),
                "title": "Birth recorded",
                "details": f"{birth.born_alive} born alive, {birth.stillborn} stillborn",
                "status": "completed",
            }
        )
    return sorted(events, key=lambda event: event["date"], reverse=True)
