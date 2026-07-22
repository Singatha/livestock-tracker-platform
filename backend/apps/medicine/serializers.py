from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.animals.models import Animal

from .models import DoseAdministration, MedicineBatch, MedicineProduct, TreatmentCourse


class MedicineProductSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = MedicineProduct
        fields = [
            "id",
            "farm",
            "name",
            "active_ingredient",
            "concentration",
            "stock_unit",
            "reorder_level",
            "meat_withdrawal_days",
            "milk_withdrawal_days",
            "instructions",
            "total_quantity",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "total_quantity",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]

    def get_total_quantity(self, obj):
        return sum((batch.quantity_on_hand for batch in obj.batches.all()), start=0)

    def get_is_low_stock(self, obj) -> bool:
        return self.get_total_quantity(obj) <= obj.reorder_level


class MedicineBatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    stock_unit = serializers.CharField(source="product.stock_unit", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = MedicineBatch
        fields = [
            "id",
            "farm",
            "product",
            "product_name",
            "batch_number",
            "expiry_date",
            "quantity_on_hand",
            "stock_unit",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "product_name",
            "stock_unit",
            "is_expired",
            "created_at",
            "updated_at",
        ]

    def validate_product(self, product):
        if product.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Product does not belong to this farm")
        return product

    def get_is_expired(self, obj) -> bool:
        return obj.expiry_date < timezone.localdate()


class TreatmentCourseSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source="animal.ear_tag", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    doses_administered = serializers.IntegerField(read_only=True)

    class Meta:
        model = TreatmentCourse
        fields = [
            "id",
            "farm",
            "animal",
            "animal_ear_tag",
            "product",
            "product_name",
            "reason",
            "dosage",
            "route",
            "started_on",
            "planned_doses",
            "frequency_hours",
            "status",
            "meat_withdrawal_end_date",
            "milk_withdrawal_end_date",
            "notes",
            "prescribed_by",
            "doses_administered",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "prescribed_by",
            "meat_withdrawal_end_date",
            "milk_withdrawal_end_date",
            "doses_administered",
            "created_at",
            "updated_at",
        ]

    def validate_animal(self, animal: Animal):
        if animal.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Animal does not belong to this farm")
        return animal

    def validate_product(self, product):
        if product.farm_id != self.context["farm"].id:
            raise serializers.ValidationError("Product does not belong to this farm")
        return product

    def validate(self, attrs):
        if self.instance is not None:
            if "animal" in attrs and attrs["animal"] != self.instance.animal:
                raise serializers.ValidationError({"animal": "Course animal cannot be changed"})
            if "product" in attrs and attrs["product"] != self.instance.product:
                raise serializers.ValidationError(
                    {"product": "Prescribed product cannot be changed"}
                )
        return attrs


class DoseAdministrationSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    product_name = serializers.CharField(source="course.product.name", read_only=True)

    class Meta:
        model = DoseAdministration
        fields = [
            "id",
            "farm",
            "course",
            "batch",
            "batch_number",
            "product_name",
            "administered_at",
            "quantity_used",
            "notes",
            "administered_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "farm",
            "batch_number",
            "product_name",
            "administered_by",
            "created_at",
        ]

    def validate(self, attrs):
        farm = self.context["farm"]
        course = attrs["course"]
        batch = attrs["batch"]
        if course.farm_id != farm.id or batch.farm_id != farm.id:
            raise serializers.ValidationError("Course and batch must belong to this farm")
        if course.status != TreatmentCourse.Status.ACTIVE:
            raise serializers.ValidationError({"course": "Only active courses accept doses"})
        if batch.product_id != course.product_id:
            raise serializers.ValidationError(
                {"batch": "Batch does not match the prescribed product"}
            )
        if batch.expiry_date < attrs["administered_at"].date():
            raise serializers.ValidationError({"batch": "Expired medicine cannot be administered"})
        if attrs["quantity_used"] <= 0:
            raise serializers.ValidationError(
                {"quantity_used": "Quantity must be greater than zero"}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        batch = MedicineBatch.objects.select_for_update().get(pk=validated_data["batch"].pk)
        if batch.quantity_on_hand < validated_data["quantity_used"]:
            raise serializers.ValidationError({"quantity_used": "Insufficient batch stock"})
        validated_data["batch"] = batch
        administration = super().create(validated_data)
        batch.quantity_on_hand -= administration.quantity_used
        batch.save(update_fields=["quantity_on_hand", "updated_at"])
        course = administration.course
        administered_date = administration.administered_at.date()
        course.meat_withdrawal_end_date = administered_date + timedelta(
            days=course.product.meat_withdrawal_days
        )
        course.milk_withdrawal_end_date = administered_date + timedelta(
            days=course.product.milk_withdrawal_days
        )
        if course.administrations.count() >= course.planned_doses:
            course.status = TreatmentCourse.Status.COMPLETED
        course.save(
            update_fields=[
                "meat_withdrawal_end_date",
                "milk_withdrawal_end_date",
                "status",
                "updated_at",
            ]
        )
        return administration
