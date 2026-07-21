from rest_framework.routers import SimpleRouter

from .views import HusbandryTaskViewSet

router = SimpleRouter()
router.register("tasks", HusbandryTaskViewSet, basename="husbandry-task")
urlpatterns = router.urls
