from rest_framework.routers import SimpleRouter

from .views import BirthRecordViewSet, BreedingRecordViewSet

router = SimpleRouter()
router.register("breedings", BreedingRecordViewSet, basename="breeding-record")
router.register("births", BirthRecordViewSet, basename="birth-record")
urlpatterns = router.urls
