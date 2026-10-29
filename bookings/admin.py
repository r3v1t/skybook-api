from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "seat_number", "passenger_last_name", "price", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("passenger_last_name", "document_number", "flight__number")
