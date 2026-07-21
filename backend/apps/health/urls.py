from rest_framework.routers import SimpleRouter

from .views import HealthObservationViewSet, TreatmentViewSet

router = SimpleRouter()
router.register("observations", HealthObservationViewSet, basename="health-observation")
router.register("treatments", TreatmentViewSet, basename="treatment")
urlpatterns = router.urls
