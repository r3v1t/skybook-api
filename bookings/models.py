from django.conf import settings
from django.db import models
from django.db.models import Q

from flights.models import Flight


class Ticket(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name="tickets")
    passenger_first_name = models.CharField(max_length=60)
    passenger_last_name = models.CharField(max_length=60)
    document_number = models.CharField(max_length=20)
    seat_number = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # A seat can be sold again only after the previous ticket was cancelled.
            models.UniqueConstraint(
                fields=["flight", "seat_number"],
                condition=Q(status="booked"),
                name="unique_booked_seat_per_flight",
            ),
        ]

    def __str__(self):
        return f"Ticket #{self.pk} {self.flight.number} seat {self.seat_number}"
