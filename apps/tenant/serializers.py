from common.constants import Regex
from common.exceptions import ApplicationException
from common.validators import ValidationMessages
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import (
    Tenant,
)
from .services.tenant import TenantService


class TenantOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "name",
            "contact_name",
            "contact_email",
            "contact_mobile",
            "address",
            "status",
            "created_name",
            "updated_name",
            "created_at",
            "updated_at",
        )


class TenantInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    contact_name = serializers.CharField(max_length=64)
    contact_email = serializers.RegexField(
        regex=Regex.EMAIL,
        error_messages={
            "invalid": ValidationMessages.INVALID_EMAIL,
        },
    )
    contact_mobile = serializers.RegexField(
        regex=Regex.MOBILE,
        error_messages={
            "invalid": ValidationMessages.INVALID_MOBILE,
        },
    )
    address = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True, default=""
    )
    status = serializers.ChoiceField(choices=Tenant.STATUS_CHOICES)

    def validate(self, attrs):
        name = attrs["name"]

        if TenantService.name_exists(name, self.instance):
            raise ApplicationException(_("租户名称已被使用"))

        if self.instance:
            if TenantService.contact_email_exists(
                self.instance, attrs["contact_email"]
            ):
                raise ApplicationException(_("邮箱已被使用"))

            if TenantService.contact_mobile_exists(
                self.instance, attrs["contact_mobile"]
            ):
                raise ApplicationException(_("电话已被使用"))

        return attrs
