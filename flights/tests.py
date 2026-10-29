from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Aircraft, Airport, Flight

User = get_user_model()


def make_flight(number="SB101", origin=None, destination=None, aircraft=None, days=2, price="100.00"):
    origin = origin or Airport.objects.get_or_create(code="WAW", defaults={"name": "Chopin", "city": "Warsaw", "country": "Poland"})[0]
    destination = destination or Airport.objects.get_or_create(code="BER", defaults={"name": "Brandenburg", "city": "Berlin", "country": "Germany"})[0]
    aircraft = aircraft or Aircraft.objects.get_or_create(registration="UR-TST", defaults={"model": "ATR 72", "capacity": 3})[0]
    departure = timezone.now() + timedelta(days=days)
    return Flight.objects.create(
        number=number,
        origin=origin,
        destination=destination,
        aircraft=aircraft,
        departure_time=departure,
        arrival_time=departure + timedelta(hours=2),
        base_price=Decimal(price),
    )


class FlightApiTests(APITestCase):
    def setUp(self):
        self.flight = make_flight()
        self.admin = User.objects.create_user("admin", password="pass12345!", is_staff=True)
        self.user = User.objects.create_user("user", password="pass12345!")

    def test_anyone_can_list_flights_with_available_seats(self):
        response = self.client.get("/api/flights/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["available_seats"], 3)

    def test_filter_by_route_and_price(self):
        vie = Airport.objects.create(code="VIE", name="Vienna", city="Vienna", country="Austria")
        make_flight(number="SB202", destination=vie, price="300.00")

        response = self.client.get("/api/flights/", {"destination": "ber", "max_price": 150})
        numbers = [f["number"] for f in response.data["results"]]
        self.assertEqual(numbers, ["SB101"])

    def test_regular_user_cannot_create_flight(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/flights/", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_creates_flight_and_same_airport_route_is_rejected(self):
        self.client.force_authenticate(self.admin)
        departure = timezone.now() + timedelta(days=5)
        payload = {
            "number": "SB999",
            "origin": "WAW",
            "destination": "BER",
            "aircraft": self.flight.aircraft.id,
            "departure_time": departure.isoformat(),
            "arrival_time": (departure + timedelta(hours=1)).isoformat(),
            "base_price": "50.00",
        }
        self.assertEqual(self.client.post("/api/flights/", payload).status_code, status.HTTP_201_CREATED)

        payload.update(number="SB998", destination="WAW")
        self.assertEqual(self.client.post("/api/flights/", payload).status_code, status.HTTP_400_BAD_REQUEST)

    def test_seats_endpoint_lists_free_seats(self):
        response = self.client.get(f"/api/flights/{self.flight.id}/seats/")
        self.assertEqual(response.data["free_seats"], [1, 2, 3])
