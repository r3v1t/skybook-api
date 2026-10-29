from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FlightReportView, TicketViewSet

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("reports/flights/", FlightReportView.as_view(), name="flight-report"),
    *router.urls,
]
