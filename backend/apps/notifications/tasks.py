from celery import shared_task


@shared_task
def generate_daily_reminders() -> int:
    from .services import generate_task_reminders

    return generate_task_reminders()


@shared_task
def send_notification_email(notification_id: str) -> None:
    from .services import deliver_notification_email

    deliver_notification_email(notification_id)
