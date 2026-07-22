from rest_framework.routers import SimpleRouter

from .views import (
    DoseAdministrationViewSet,
    MedicineBatchViewSet,
    MedicineProductViewSet,
    TreatmentCourseViewSet,
)

router = SimpleRouter()
router.register("products", MedicineProductViewSet, basename="medicine-product")
router.register("batches", MedicineBatchViewSet, basename="medicine-batch")
router.register("courses", TreatmentCourseViewSet, basename="treatment-course")
router.register("administrations", DoseAdministrationViewSet, basename="dose-administration")
urlpatterns = router.urls
