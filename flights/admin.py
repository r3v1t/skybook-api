from django.contrib import admin

from .models import Aircraft, Airport, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "country")
    search_fields = ("code", "name", "city")


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ("registration", "model", "capacity")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("number", "origin", "destination", "departure_time", "base_price", "status")
    list_filter = ("status", "origin", "destination")
    search_fields = ("number",)
