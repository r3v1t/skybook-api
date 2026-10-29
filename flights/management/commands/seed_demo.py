from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from flights.models import Aircraft, Airport, Flight

AIRPORTS = [
    ("KBP", "Boryspil International", "Kyiv", "Ukraine"),
    ("LWO", "Lviv Danylo Halytskyi", "Lviv", "Ukraine"),
    ("WAW", "Warsaw Chopin", "Warsaw", "Poland"),
    ("BER", "Berlin Brandenburg", "Berlin", "Germany"),
    ("VIE", "Vienna International", "Vienna", "Austria"),
]

AIRCRAFT = [
    ("UR-PSA", "Boeing 737-800", 186),
    ("UR-EMA", "Embraer E195", 120),
    ("SP-LWA", "ATR 72-600", 70),
]

ROUTES = [
    ("SB101", "WAW", "BER", "UR-PSA", Decimal("89.00"), timedelta(hours=1, minutes=35)),
    ("SB202", "WAW", "VIE", "UR-EMA", Decimal("110.00"), timedelta(hours=1, minutes=25)),
    ("SB303", "BER", "VIE", "SP-LWA", Decimal("75.50"), timedelta(hours=1, minutes=15)),
    ("SB404", "VIE", "WAW", "UR-EMA", Decimal("99.90"), timedelta(hours=1, minutes=20)),
]


class Command(BaseCommand):
    help = "Fill the database with demo airports, aircraft and flights for the next 7 days."

    def handle(self, *args, **options):
        airports = {
            code: Airport.objects.get_or_create(code=code, defaults={"name": n, "city": c, "country": co})[0]
            for code, n, c, co in AIRPORTS
        }
        aircraft = {
            reg: Aircraft.objects.get_or_create(registration=reg, defaults={"model": m, "capacity": cap})[0]
            for reg, m, cap in AIRCRAFT
        }

        start = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        created = 0
        for day in range(7):
            for i, (number, origin, dest, reg, price, duration) in enumerate(ROUTES):
                departure = start + timedelta(days=day, hours=i * 3)
                _, is_new = Flight.objects.get_or_create(
                    number=number,
                    departure_time=departure,
                    defaults={
                        "origin": airports[origin],
                        "destination": airports[dest],
                        "aircraft": aircraft[reg],
                        "arrival_time": departure + duration,
                        "base_price": price,
                    },
                )
                created += is_new

        self.stdout.write(self.style.SUCCESS(f"Demo data ready: {created} new flights."))
