from django.db import models
from django.db.models import F, Q


class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="IATA code, e.g. KBP")
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=80)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.city})"


class Aircraft(models.Model):
    registration = models.CharField(max_length=10, unique=True)
    model = models.CharField(max_length=60)
    capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ["registration"]
        verbose_name_plural = "aircraft"

    def __str__(self):
        return f"{self.model} {self.registration}"


class Flight(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    number = models.CharField(max_length=10)
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="arrivals")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        ordering = ["departure_time"]
        constraints = [
            models.UniqueConstraint(fields=["number", "departure_time"], name="unique_flight_departure"),
            models.CheckConstraint(condition=~Q(origin=F("destination")), name="origin_not_destination"),
            models.CheckConstraint(condition=Q(arrival_time__gt=F("departure_time")), name="arrival_after_departure"),
            models.CheckConstraint(condition=Q(base_price__gte=0), name="price_not_negative"),
        ]

    def __str__(self):
        return f"{self.number} {self.origin.code}->{self.destination.code} {self.departure_time:%Y-%m-%d %H:%M}"
