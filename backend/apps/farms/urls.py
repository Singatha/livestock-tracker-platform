from rest_framework.routers import SimpleRouter

from .views import FarmViewSet

router = SimpleRouter()
router.register("", FarmViewSet, basename="farm")
urlpatterns = router.urls
