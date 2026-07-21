from apps.health.models import HealthObservation, Treatment
from apps.husbandry.models import HusbandryTask

from .models import Animal


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
    return sorted(events, key=lambda event: event["date"], reverse=True)
