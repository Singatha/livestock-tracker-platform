import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animals", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AnimalLifecycleEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("registered", "Registered"),
                            ("status_changed", "Status changed"),
                            ("flock_transferred", "Flock transferred"),
                        ],
                        max_length=30,
                    ),
                ),
                ("effective_date", models.DateField()),
                (
                    "from_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("active", "Active"),
                            ("sold", "Sold"),
                            ("deceased", "Deceased"),
                            ("missing", "Missing"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "to_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("active", "Active"),
                            ("sold", "Sold"),
                            ("deceased", "Deceased"),
                            ("missing", "Missing"),
                        ],
                        max_length=20,
                    ),
                ),
                ("reason", models.CharField(blank=True, max_length=250)),
                (
                    "animal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lifecycle_events",
                        to="animals.animal",
                    ),
                ),
                (
                    "farm",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="animal_lifecycle_events",
                        to="farms.farm",
                    ),
                ),
                (
                    "from_flock",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lifecycle_events_from",
                        to="animals.flock",
                    ),
                ),
                (
                    "recorded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="recorded_animal_lifecycle_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "to_flock",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lifecycle_events_to",
                        to="animals.flock",
                    ),
                ),
            ],
            options={
                "ordering": ["-effective_date", "-created_at"],
                "indexes": [
                    models.Index(
                        fields=["farm", "event_type", "effective_date"],
                        name="animals_ani_farm_id_6c53ca_idx",
                    )
                ],
            },
        ),
    ]
