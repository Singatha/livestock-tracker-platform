import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("farms", "0001_initial"),
        ("husbandry", "0002_husbandrytask_reminder_days_before"),
    ]
    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("kind", models.CharField(choices=[("task_due", "Task due soon"), ("task_overdue", "Task overdue")], max_length=30)),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("link", models.CharField(default="/tasks", max_length=255)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("farm", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="farms.farm")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="husbandry.husbandrytask")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="notification", constraint=models.UniqueConstraint(fields=("recipient", "task", "kind"), name="unique_task_notification")),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["farm", "recipient", "read_at"], name="notificatio_farm_id_e18e02_idx")),
    ]
