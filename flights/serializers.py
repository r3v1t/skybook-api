from rest_framework import serializers

from .models import Aircraft, Airport, Flight


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "code", "name", "city", "country")

    def validate_code(self, value):
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("IATA code must be 3 letters.")
        return value.upper()


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = ("id", "registration", "model", "capacity")


class FlightSerializer(serializers.ModelSerializer):
    origin = serializers.SlugRelatedField(slug_field="code", queryset=Airport.objects.all())
    destination = serializers.SlugRelatedField(slug_field="code", queryset=Airport.objects.all())
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "origin",
            "destination",
            "aircraft",
            "departure_time",
            "arrival_time",
            "base_price",
            "status",
            "available_seats",
        )

    def validate(self, attrs):
        origin = attrs.get("origin", getattr(self.instance, "origin", None))
        destination = attrs.get("destination", getattr(self.instance, "destination", None))
        departure = attrs.get("departure_time", getattr(self.instance, "departure_time", None))
        arrival = attrs.get("arrival_time", getattr(self.instance, "arrival_time", None))
        if origin == destination:
            raise serializers.ValidationError("Origin and destination must be different.")
        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError("Arrival must be after departure.")
        return attrs
