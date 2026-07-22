from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.farms.permissions import FarmManagerRecordPermission
from apps.farms.viewsets import FarmScopedModelViewSet

from .models import DoseAdministration, MedicineBatch, MedicineProduct, TreatmentCourse
from .serializers import (
    DoseAdministrationSerializer,
    MedicineBatchSerializer,
    MedicineProductSerializer,
    TreatmentCourseSerializer,
)


class MedicineProductViewSet(FarmScopedModelViewSet):
    queryset = MedicineProduct.objects.none()
    serializer_class = MedicineProductSerializer
    permission_classes = [FarmManagerRecordPermission]

    def get_queryset(self):
        return MedicineProduct.objects.filter(farm=self.farm).prefetch_related("batches")


class MedicineBatchViewSet(FarmScopedModelViewSet):
    queryset = MedicineBatch.objects.none()
    serializer_class = MedicineBatchSerializer
    permission_classes = [FarmManagerRecordPermission]

    def get_queryset(self):
        queryset = MedicineBatch.objects.filter(farm=self.farm).select_related("product")
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if self.request.query_params.get("expiring") == "true":
            today = timezone.localdate()
            queryset = queryset.filter(expiry_date__range=(today, today + timedelta(days=30)))
        return queryset


class TreatmentCourseViewSet(FarmScopedModelViewSet):
    queryset = TreatmentCourse.objects.none()
    serializer_class = TreatmentCourseSerializer

    def get_queryset(self):
        queryset = (
            TreatmentCourse.objects.filter(farm=self.farm)
            .select_related("animal", "product", "prescribed_by")
            .annotate(doses_administered=Count("administrations"))
        )
        animal_id = self.request.query_params.get("animal")
        status = self.request.query_params.get("status")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, prescribed_by=self.request.user)


class DoseAdministrationViewSet(FarmScopedModelViewSet):
    queryset = DoseAdministration.objects.none()
    serializer_class = DoseAdministrationSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = DoseAdministration.objects.filter(farm=self.farm).select_related(
            "course", "course__animal", "course__product", "batch", "administered_by"
        )
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(farm=self.farm, administered_by=self.request.user)
