from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source="flight.number", read_only=True)
    departure_time = serializers.DateTimeField(source="flight.departure_time", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "flight",
            "flight_number",
            "departure_time",
            "seat_number",
            "passenger_first_name",
            "passenger_last_name",
            "document_number",
            "price",
            "status",
            "created_at",
        )
        read_only_fields = ("price", "status", "created_at")
        # Seat availability is checked in services.book_ticket under a row lock.
        validators = []


class FlightReportSerializer(serializers.Serializer):
    flight_id = serializers.IntegerField()
    number = serializers.CharField()
    route = serializers.CharField()
    departure_time = serializers.DateTimeField()
    capacity = serializers.IntegerField()
    tickets_sold = serializers.IntegerField()
    occupancy_percent = serializers.FloatField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
