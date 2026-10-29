"""Business logic for booking and cancelling tickets.

Kept out of views so it can be tested and reused on its own.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from flights.models import Flight

from .models import Ticket


@transaction.atomic
def book_ticket(*, user, flight_id, seat_number, passenger_first_name, passenger_last_name, document_number):
    # Lock the flight row so two users cannot buy the last seat at the same time.
    flight = Flight.objects.select_for_update().select_related("aircraft").get(pk=flight_id)

    if flight.status != Flight.Status.SCHEDULED:
        raise ValidationError({"flight": "Flight is not open for booking."})
    if flight.departure_time <= timezone.now():
        raise ValidationError({"flight": "Flight has already departed."})
    if not 1 <= seat_number <= flight.aircraft.capacity:
        raise ValidationError({"seat_number": f"Seat must be between 1 and {flight.aircraft.capacity}."})

    booked = flight.tickets.filter(status=Ticket.Status.BOOKED)
    if booked.filter(seat_number=seat_number).exists():
        raise ValidationError({"seat_number": "Seat is already taken."})

    return Ticket.objects.create(
        user=user,
        flight=flight,
        seat_number=seat_number,
        passenger_first_name=passenger_first_name,
        passenger_last_name=passenger_last_name,
        document_number=document_number,
        price=flight.base_price,
    )


@transaction.atomic
def cancel_ticket(ticket: Ticket) -> Ticket:
    ticket = Ticket.objects.select_for_update().select_related("flight").get(pk=ticket.pk)
    if ticket.status == Ticket.Status.CANCELLED:
        raise ValidationError({"status": "Ticket is already cancelled."})
    if ticket.flight.departure_time <= timezone.now():
        raise ValidationError({"flight": "Cannot cancel a ticket after departure."})
    ticket.status = Ticket.Status.CANCELLED
    ticket.save(update_fields=["status"])
    return ticket
