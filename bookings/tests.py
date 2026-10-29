from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from flights.models import Flight
from flights.tests import make_flight

from .models import Ticket

User = get_user_model()


class TicketApiTests(APITestCase):
    def setUp(self):
        self.flight = make_flight()  # capacity 3, price 100.00
        self.user = User.objects.create_user("user", password="pass12345!")
        self.other = User.objects.create_user("other", password="pass12345!")
        self.admin = User.objects.create_user("admin", password="pass12345!", is_staff=True)

    def book(self, user, seat=1, flight=None):
        self.client.force_authenticate(user)
        return self.client.post(
            "/api/tickets/",
            {
                "flight": (flight or self.flight).id,
                "seat_number": seat,
                "passenger_first_name": "Roman",
                "passenger_last_name": "Popovych",
                "document_number": "AB123456",
            },
        )

    def test_booking_requires_authentication(self):
        response = self.client.post("/api/tickets/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_ticket_copies_flight_price(self):
        response = self.book(self.user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["price"], "100.00")
        self.assertEqual(response.data["status"], "booked")

    def test_same_seat_cannot_be_booked_twice(self):
        self.book(self.user, seat=2)
        response = self.book(self.other, seat=2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat_number", response.data)

    def test_seat_outside_capacity_is_rejected(self):
        response = self.book(self.user, seat=4)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_departed_or_cancelled_flight(self):
        past = make_flight(number="SB000", days=-1)
        self.assertEqual(self.book(self.user, flight=past).status_code, status.HTTP_400_BAD_REQUEST)

        self.flight.status = Flight.Status.CANCELLED
        self.flight.save()
        self.assertEqual(self.book(self.user).status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelled_seat_can_be_booked_again(self):
        ticket_id = self.book(self.user, seat=1).data["id"]
        response = self.client.post(f"/api/tickets/{ticket_id}/cancel/")
        self.assertEqual(response.data["status"], "cancelled")

        self.assertEqual(self.book(self.other, seat=1).status_code, status.HTTP_201_CREATED)

    def test_cancel_twice_is_rejected(self):
        ticket_id = self.book(self.user).data["id"]
        self.client.post(f"/api/tickets/{ticket_id}/cancel/")
        response = self.client.post(f"/api/tickets/{ticket_id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_users_see_only_their_own_tickets(self):
        self.book(self.user, seat=1)
        other_id = self.book(self.other, seat=2).data["id"]

        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get("/api/tickets/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/tickets/{other_id}/").status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get("/api/tickets/").data["count"], 2)

    def test_available_seats_and_report_reflect_bookings(self):
        self.book(self.user, seat=1)
        self.book(self.other, seat=2)

        flight = self.client.get(f"/api/flights/{self.flight.id}/").data
        self.assertEqual(flight["available_seats"], 1)

        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get("/api/reports/flights/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        row = self.client.get("/api/reports/flights/").data[0]
        self.assertEqual(row["tickets_sold"], 2)
        self.assertEqual(row["occupancy_percent"], 66.7)
        self.assertEqual(row["revenue"], "200.00")
        self.assertEqual(Ticket.objects.count(), 2)


class AuthApiTests(APITestCase):
    def test_register_login_and_me(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "roman", "email": "roman@example.com", "password": "Str0ng-pass-2026"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        tokens = self.client.post("/api/auth/token/", {"username": "roman", "password": "Str0ng-pass-2026"}).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        self.assertEqual(self.client.get("/api/auth/me/").data["username"], "roman")

    def test_weak_password_is_rejected(self):
        response = self.client.post("/api/auth/register/", {"username": "roman", "password": "123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
