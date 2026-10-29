from django.db.models import Count, F, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import FlightFilter
from .models import Aircraft, Airport, Flight
from .permissions import IsAdminOrReadOnly
from .serializers import AircraftSerializer, AirportSerializer, FlightSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["code", "name", "city", "country"]


class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [IsAdminOrReadOnly]


class FlightViewSet(viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = FlightFilter
    ordering_fields = ["departure_time", "base_price", "available_seats"]
    search_fields = ["number", "origin__city", "destination__city"]

    def get_queryset(self):
        return (
            Flight.objects.select_related("origin", "destination", "aircraft")
            .annotate(
                available_seats=F("aircraft__capacity")
                - Count("tickets", filter=Q(tickets__status="booked"))
            )
            .order_by("departure_time", "id")
        )

    @action(detail=True, methods=["get"])
    def seats(self, request, pk=None):
        """List free seat numbers for a flight."""
        flight = self.get_object()
        taken = set(
            flight.tickets.filter(status="booked").values_list("seat_number", flat=True)
        )
        free = [n for n in range(1, flight.aircraft.capacity + 1) if n not in taken]
        return Response({"flight": flight.id, "free_seats": free})
