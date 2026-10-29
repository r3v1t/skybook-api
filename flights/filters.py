import django_filters

from .models import Flight


class FlightFilter(django_filters.FilterSet):
    origin = django_filters.CharFilter(field_name="origin__code", lookup_expr="iexact")
    destination = django_filters.CharFilter(field_name="destination__code", lookup_expr="iexact")
    date = django_filters.DateFilter(field_name="departure_time", lookup_expr="date")
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")
    min_seats = django_filters.NumberFilter(field_name="available_seats", lookup_expr="gte")

    class Meta:
        model = Flight
        fields = ["status"]
