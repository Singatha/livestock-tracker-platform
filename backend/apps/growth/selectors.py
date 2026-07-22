from decimal import Decimal

from apps.animals.models import Animal


def animal_growth_summary(farm):
    summaries = []
    animals = Animal.objects.filter(farm=farm, weight_measurements__isnull=False).distinct()
    for animal in animals.select_related("flock"):
        measurements = list(animal.weight_measurements.all()[:2])
        latest = measurements[0]
        previous = measurements[1] if len(measurements) > 1 else None
        change = latest.weight_kg - previous.weight_kg if previous else None
        days = (latest.measured_on - previous.measured_on).days if previous else 0
        daily_gain = change / Decimal(days) if change is not None and days > 0 else None
        summaries.append(
            {
                "animal": animal.id,
                "ear_tag": animal.ear_tag,
                "name": animal.name,
                "flock_name": animal.flock.name if animal.flock else None,
                "latest_weight_kg": latest.weight_kg,
                "latest_measured_on": latest.measured_on,
                "previous_weight_kg": previous.weight_kg if previous else None,
                "change_kg": change,
                "average_daily_gain_kg": daily_gain,
            }
        )
    return sorted(summaries, key=lambda item: item["latest_measured_on"], reverse=True)


def weight_loss_count(farm):
    return sum(1 for item in animal_growth_summary(farm) if (item["change_kg"] or 0) < 0)
