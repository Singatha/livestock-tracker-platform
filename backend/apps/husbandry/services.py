from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import HusbandryTask


@transaction.atomic
def complete_task(
    *, task: HusbandryTask, completed_by, completion_notes: str = ""
) -> HusbandryTask:
    if task.status != HusbandryTask.Status.SCHEDULED:
        raise ValueError("Only scheduled tasks can be completed")

    task.status = HusbandryTask.Status.COMPLETED
    task.completed_at = timezone.now()
    task.completed_by = completed_by
    task.completion_notes = completion_notes
    task.save(
        update_fields=["status", "completed_at", "completed_by", "completion_notes", "updated_at"]
    )

    if task.recurrence_days:
        HusbandryTask.objects.create(
            farm=task.farm,
            animal=task.animal,
            flock=task.flock,
            task_type=task.task_type,
            title=task.title,
            due_date=task.due_date + timedelta(days=task.recurrence_days),
            recurrence_days=task.recurrence_days,
            notes=task.notes,
        )
    return task
