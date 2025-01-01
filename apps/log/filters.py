from django_filters.rest_framework import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    NumberFilter,
)

from .models import RequestLog


class RequestLogFilter(FilterSet):
    api_path = CharFilter(lookup_expr="icontains")
    client_ip = CharFilter()
    status_code = CharFilter()
    user_id = CharFilter()
    system = CharFilter()
    module = CharFilter()
    duration_gte = NumberFilter(field_name="duration", lookup_expr="gte")
    request_id = CharFilter()
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = RequestLog
        fields = (
            "api_path",
            "client_ip",
            "status_code",
            "user_id",
            "system",
            "module",
            "duration_gte",
            "request_id",
            "created_at_lte",
            "created_at_gte",
        )
