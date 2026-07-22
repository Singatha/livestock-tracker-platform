from pathlib import Path

from django.conf import settings
from django.db import models

from apps.animals.models import Animal
from apps.common.models import TimeStampedModel
from apps.farms.models import Farm


def attachment_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"attachments/{instance.farm_id}/{instance.id}{extension}"


class Attachment(TimeStampedModel):
    class Category(models.TextChoices):
        PHOTO = "photo", "Animal photo"
        VETERINARY = "veterinary", "Veterinary document"
        PRESCRIPTION = "prescription", "Prescription"
        LAB_RESULT = "lab_result", "Lab result"
        CERTIFICATE = "certificate", "Certificate"
        INVOICE = "invoice", "Invoice"
        OTHER = "other", "Other"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="attachments")
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=attachment_path, max_length=500)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveBigIntegerField()
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_attachments",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["farm", "category", "created_at"]),
            models.Index(fields=["farm", "animal", "created_at"]),
        ]

    def __str__(self):
        return self.title
