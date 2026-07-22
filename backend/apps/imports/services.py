import csv
import io
from contextlib import nullcontext

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.animals.models import Animal, Flock
from apps.animals.serializers import AnimalSerializer, FlockSerializer
from apps.animals.services import register_lifecycle_event
from apps.growth.serializers import WeightMeasurementSerializer
from apps.medicine.models import MedicineProduct
from apps.medicine.serializers import MedicineBatchSerializer

from .models import ImportJob

TEMPLATES = {
    ImportJob.Kind.FLOCKS: ["name", "description"],
    ImportJob.Kind.ANIMALS: [
        "ear_tag",
        "name",
        "species",
        "breed",
        "sex",
        "date_of_birth",
        "flock",
        "status",
        "needs_attention",
        "notes",
    ],
    ImportJob.Kind.WEIGHTS: [
        "ear_tag",
        "measured_on",
        "weight_kg",
        "body_condition_score",
        "notes",
    ],
    ImportJob.Kind.MEDICINE_BATCHES: [
        "product",
        "batch_number",
        "expiry_date",
        "quantity_on_hand",
    ],
}


def template_csv(kind):
    output = io.StringIO()
    csv.writer(output).writerow(TEMPLATES[kind])
    return output.getvalue()


def parse_csv(upload, kind):
    try:
        content = upload.read().decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValidationError({"file": "CSV must use UTF-8 encoding"}) from error
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None:
        raise ValidationError({"file": "CSV is empty"})
    missing = [field for field in TEMPLATES[kind] if field not in reader.fieldnames]
    if missing:
        raise ValidationError({"file": f"Missing columns: {', '.join(missing)}"})
    rows = []
    for number, raw in enumerate(reader, start=2):
        if not any((value or "").strip() for value in raw.values()):
            continue
        rows.append(
            {"row": number, "data": {key: (raw.get(key) or "").strip() for key in TEMPLATES[kind]}}
        )
    if len(rows) > 5000:
        raise ValidationError({"file": "CSV may contain at most 5,000 data rows"})
    return rows


def serializer_for_row(*, job, row):
    data = dict(row["data"])
    context = {"farm": job.farm}
    if job.kind == ImportJob.Kind.FLOCKS:
        return FlockSerializer(data=data, context=context)
    if job.kind == ImportJob.Kind.ANIMALS:
        flock_name = data.pop("flock", "")
        flock = Flock.objects.filter(farm=job.farm, name__iexact=flock_name).first()
        if flock_name and flock is None:
            raise ValidationError({"flock": "Flock was not found in this farm"})
        data["flock"] = str(flock.id) if flock else None
        for optional in ("date_of_birth",):
            data[optional] = data[optional] or None
        if not data["status"]:
            data["status"] = Animal.Status.ACTIVE
        if not data["sex"]:
            data["sex"] = Animal.Sex.UNKNOWN
        if data["needs_attention"] == "":
            data["needs_attention"] = False
        return AnimalSerializer(data=data, context=context)
    if job.kind == ImportJob.Kind.WEIGHTS:
        ear_tag = data.pop("ear_tag")
        animal = Animal.objects.filter(farm=job.farm, ear_tag__iexact=ear_tag).first()
        if animal is None:
            raise ValidationError({"ear_tag": "Animal was not found in this farm"})
        data["animal"] = str(animal.id)
        data["body_condition_score"] = data["body_condition_score"] or None
        return WeightMeasurementSerializer(data=data, context=context)
    product_name = data.pop("product")
    product = MedicineProduct.objects.filter(farm=job.farm, name__iexact=product_name).first()
    if product is None:
        raise ValidationError({"product": "Medicine product was not found in this farm"})
    data["product"] = str(product.id)
    return MedicineBatchSerializer(data=data, context=context)


def error_detail(error):
    return error.detail if isinstance(error, ValidationError) else str(error)


def validate_rows(job):
    errors = []
    seen = set()
    duplicate_key = {
        ImportJob.Kind.FLOCKS: "name",
        ImportJob.Kind.ANIMALS: "ear_tag",
        ImportJob.Kind.WEIGHTS: None,
        ImportJob.Kind.MEDICINE_BATCHES: "batch_number",
    }[job.kind]
    for row in job.rows:
        key = row["data"].get(duplicate_key, "").lower() if duplicate_key else ""
        if key and key in seen:
            errors.append({"row": row["row"], "errors": {duplicate_key: ["Duplicate in CSV"]}})
            continue
        seen.add(key)
        try:
            serializer = serializer_for_row(job=job, row=row)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            errors.append({"row": row["row"], "errors": error_detail(error)})
    return errors


def create_preview(*, farm, user, upload, kind, mode):
    job = ImportJob.objects.create(
        farm=farm,
        kind=kind,
        mode=mode,
        original_filename=upload.name,
        rows=parse_csv(upload, kind),
        created_by=user,
    )
    job.rows_total = len(job.rows)
    job.errors = validate_rows(job)
    job.rows_failed = len(job.errors)
    job.save(update_fields=["rows_total", "errors", "rows_failed", "updated_at"])
    return job


def save_row(*, job, row, user):
    serializer = serializer_for_row(job=job, row=row)
    serializer.is_valid(raise_exception=True)
    if job.kind == ImportJob.Kind.FLOCKS:
        return serializer.save(farm=job.farm)
    if job.kind == ImportJob.Kind.ANIMALS:
        animal = serializer.save(farm=job.farm)
        register_lifecycle_event(animal=animal, recorded_by=user)
        return animal
    if job.kind == ImportJob.Kind.WEIGHTS:
        return serializer.save(farm=job.farm, recorded_by=user)
    return serializer.save(farm=job.farm)


def commit_import(*, job, user):
    if job.status != ImportJob.Status.PREVIEWED:
        raise ValidationError("Only previewed imports can be committed")
    if job.mode == ImportJob.Mode.ALL_OR_NOTHING and job.errors:
        raise ValidationError("Resolve all preview errors before committing this import")
    preview_invalid = {error["row"] for error in job.errors}
    succeeded = 0
    errors = list(job.errors)
    outer = transaction.atomic() if job.mode == ImportJob.Mode.ALL_OR_NOTHING else nullcontext()
    with outer:
        for row in job.rows:
            if row["row"] in preview_invalid:
                continue
            try:
                with transaction.atomic():
                    save_row(job=job, row=row, user=user)
                succeeded += 1
            except Exception as error:
                if job.mode == ImportJob.Mode.ALL_OR_NOTHING:
                    raise
                errors.append({"row": row["row"], "errors": error_detail(error)})
    job.status = ImportJob.Status.COMPLETED
    job.rows_succeeded = succeeded
    job.rows_failed = len(errors)
    job.errors = errors
    job.completed_at = timezone.now()
    job.save(
        update_fields=[
            "status",
            "rows_succeeded",
            "rows_failed",
            "errors",
            "completed_at",
            "updated_at",
        ]
    )
    return job
