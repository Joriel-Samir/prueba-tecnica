from rest_framework.routers import SimpleRouter

from .views import ActividadViewSet

router = SimpleRouter()
router.register("", ActividadViewSet, basename="actividad")

urlpatterns = router.urls
