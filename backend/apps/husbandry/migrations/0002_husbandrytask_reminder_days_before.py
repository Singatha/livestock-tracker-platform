from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("husbandry", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="husbandrytask",
            name="reminder_days_before",
            field=models.PositiveSmallIntegerField(default=1),
        )
    ]
