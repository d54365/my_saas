from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
)

from .models import (
    Department,
    Permission,
    Role,
    SystemUser,
)


class SystemUserFilter(FilterSet):
    username = CharFilter(lookup_expr="icontains")
    nickname = CharFilter(lookup_expr="icontains")
    email = CharFilter(lookup_expr="icontains")
    mobile = CharFilter(lookup_expr="icontains")
    is_active = BooleanFilter()
    is_super = BooleanFilter()
    last_login_at_gte = DateTimeFilter(field_name="last_login_at", lookup_expr="gte")
    last_login_at_lte = DateTimeFilter(field_name="last_login_at", lookup_expr="lte")

    class Meta:
        model = SystemUser
        fields = (
            "username",
            "nickname",
            "email",
            "mobile",
            "is_active",
            "is_super",
            "last_login_at_gte",
            "last_login_at_lte",
        )


class DepartmentFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")
    path = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Department
        fields = ("name", "path")


class PermissionFilter(FilterSet):
    code = CharFilter(lookup_expr="icontains")
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Permission
        fields = ("code", "name")


class RoleFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Role
        fields = ("name",)
