from django.core.management.base import BaseCommand

from apps.notifications.services import generate_task_reminders


class Command(BaseCommand):
    help = "Generate due and overdue husbandry task reminders"

    def handle(self, *args, **options):
        count = generate_task_reminders()
        self.stdout.write(self.style.SUCCESS(f"Created {count} reminders"))
