from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from .models import MedicineBatch, MedicineProduct, TreatmentCourse


def medicine_dashboard_counts(farm):
    today = timezone.localdate()
    low_stock = 0
    for product in MedicineProduct.objects.filter(farm=farm).prefetch_related("batches"):
        quantity = sum((batch.quantity_on_hand for batch in product.batches.all()), start=0)
        if quantity <= product.reorder_level:
            low_stock += 1
    return {
        "active_treatment_courses": TreatmentCourse.objects.filter(
            farm=farm, status=TreatmentCourse.Status.ACTIVE
        ).count(),
        "low_stock_medicines": low_stock,
        "expiring_medicine_batches": MedicineBatch.objects.filter(
            farm=farm, expiry_date__range=(today, today + timedelta(days=30))
        ).count(),
        "animals_under_withdrawal": TreatmentCourse.objects.filter(farm=farm)
        .filter(Q(meat_withdrawal_end_date__gte=today) | Q(milk_withdrawal_end_date__gte=today))
        .values("animal_id")
        .distinct()
        .count(),
    }
