from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import GrowthSummaryView, WeightMeasurementViewSet

router = SimpleRouter()
router.register("weights", WeightMeasurementViewSet, basename="weight-measurement")
urlpatterns = [path("summary/", GrowthSummaryView.as_view(), name="growth-summary"), *router.urls]
