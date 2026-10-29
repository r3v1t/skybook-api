from rest_framework.routers import DefaultRouter

from .views import AircraftViewSet, AirportViewSet, FlightViewSet

router = DefaultRouter()
router.register("airports", AirportViewSet)
router.register("aircraft", AircraftViewSet)
router.register("flights", FlightViewSet, basename="flight")

urlpatterns = router.urls
