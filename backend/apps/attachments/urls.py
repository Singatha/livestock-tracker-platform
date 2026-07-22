from rest_framework.routers import SimpleRouter

from .views import AttachmentViewSet

router = SimpleRouter()
router.register("", AttachmentViewSet, basename="attachment")
urlpatterns = router.urls
