from django_filters.rest_framework import (
    CharFilter,
    ChoiceFilter,
    FilterSet,
)

from .models import (
    Tenant,
)


class TenantFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=Tenant.STATUS_CHOICES)

    class Meta:
        model = Tenant
        fields = (
            "name",
            "status",
        )
