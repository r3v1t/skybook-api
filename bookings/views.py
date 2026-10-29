from decimal import Decimal

from django.db.models import Count, Q, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from flights.models import Flight

from .models import Ticket
from .serializers import FlightReportSerializer, TicketSerializer
from .services import book_ticket, cancel_ticket


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Users see and manage their own tickets; staff see all tickets."""

    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "flight"]

    def get_queryset(self):
        qs = Ticket.objects.select_related("flight")
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ticket = book_ticket(
            user=request.user,
            flight_id=data["flight"].pk,
            seat_number=data["seat_number"],
            passenger_first_name=data["passenger_first_name"],
            passenger_last_name=data["passenger_last_name"],
            document_number=data["document_number"],
        )
        return Response(self.get_serializer(ticket).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        ticket = cancel_ticket(self.get_object())
        return Response(self.get_serializer(ticket).data)


class FlightReportView(APIView):
    """Sales report per flight: tickets sold, occupancy and revenue (staff only)."""

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses=FlightReportSerializer(many=True))
    def get(self, request):
        booked = Q(tickets__status=Ticket.Status.BOOKED)
        flights = (
            Flight.objects.select_related("origin", "destination", "aircraft")
            .annotate(sold=Count("tickets", filter=booked), revenue=Sum("tickets__price", filter=booked))
            .order_by("departure_time")
        )
        rows = [
            {
                "flight_id": f.id,
                "number": f.number,
                "route": f"{f.origin.code}-{f.destination.code}",
                "departure_time": f.departure_time,
                "capacity": f.aircraft.capacity,
                "tickets_sold": f.sold,
                "occupancy_percent": round(f.sold / f.aircraft.capacity * 100, 1),
                "revenue": f.revenue or Decimal("0.00"),
            }
            for f in flights
        ]
        return Response(FlightReportSerializer(rows, many=True).data)
