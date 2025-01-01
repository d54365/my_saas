from django_filters.rest_framework import (
    DateTimeFilter,
    FilterSet,
)

from .models import CeleryTaskResult


class CeleryTaskResultFilter(FilterSet):
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = CeleryTaskResult
        fields = (
            "created_at_gte",
            "created_at_lte",
        )
