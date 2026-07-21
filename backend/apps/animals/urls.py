from rest_framework.routers import SimpleRouter

from .views import AnimalViewSet, FlockViewSet

router = SimpleRouter()
router.register("flocks", FlockViewSet, basename="flock")
router.register("", AnimalViewSet, basename="animal")
urlpatterns = router.urls
