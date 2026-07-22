from rest_framework.routers import SimpleRouter

from .views import FeedingPlanViewSet, FeedViewSet

router = SimpleRouter()
router.register("feeds", FeedViewSet, basename="feed")
router.register("plans", FeedingPlanViewSet, basename="feeding-plan")
urlpatterns = router.urls
