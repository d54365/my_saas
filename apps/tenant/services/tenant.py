from typing import Optional

from accounts.models import SystemUser
from common.utils import generate_random_password
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from tenant.constants import TenantConstant
from tenant.models import Tenant, TenantUser


class TenantService:
    TENANT_KEY_TEMPLATE = "tenant:{id}"
    TENANT_KEY_TIMEOUT = 60 * 60 * 24 * 30

    @classmethod
    def get_by_id(cls, tenant_id: int) -> Optional[Tenant]:
        key = cls.TENANT_KEY_TEMPLATE.format(id=tenant_id)
        instance = cache.get(key)
        if instance:
            return instance

        try:
            instance = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return None

        cache.set(key, instance, cls.TENANT_KEY_TIMEOUT)
        return instance

    @staticmethod
    def name_exists(name: str, instance: Optional[Tenant] = None) -> bool:
        queryset = Tenant.objects.filter(name=name)
        if instance:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @staticmethod
    def contact_email_exists(instance: Tenant, contact_email) -> bool:
        return (
            TenantUser.objects.all_tenants()
            .filter(
                tenant_id=instance.id,
                email=contact_email,
            )
            .exclude(username=TenantConstant.SUPER_USERNAME)
            .exists()
        )

    @staticmethod
    def contact_mobile_exists(instance: Tenant, contact_mobile) -> bool:
        return (
            TenantUser.objects.all_tenants()
            .filter(
                tenant_id=instance.id,
                email=contact_mobile,
            )
            .exclude(username=TenantConstant.SUPER_USERNAME)
            .exists()
        )

    @staticmethod
    def all() -> QuerySet:
        return Tenant.objects.all().order_by("-id")

    @staticmethod
    @transaction.atomic
    def create(
        tenant_data: dict,
        created: Optional[SystemUser] = None,
    ) -> Tenant:
        tenant = Tenant.objects.create(
            name=tenant_data["name"],
            contact_name=tenant_data["contact_name"],
            contact_email=tenant_data["contact_email"],
            contact_mobile=tenant_data["contact_mobile"],
            address=tenant_data["address"],
            status=tenant_data["status"],
            created=created,
            created_name=created.nickname if created else "",
        )

        password = generate_random_password()
        tenant_user = TenantUser(
            tenant_id=tenant.id,
            username=TenantConstant.SUPER_USERNAME,
            password=make_password(password),
            name=tenant_data["contact_name"],
            email=tenant_data["contact_email"],
            mobile=tenant_data["contact_mobile"],
            is_super=True,
            is_active=True,
        )
        tenant_user.save()
        return tenant

    @staticmethod
    @transaction.atomic
    def update(
        instance: Tenant, tenant_data: dict, updated: Optional[SystemUser] = None
    ) -> Tenant:
        instance.name = tenant_data["name"]
        instance.contact_name = tenant_data["contact_name"]
        instance.contact_email = tenant_data["contact_email"]
        instance.contact_mobile = tenant_data["contact_mobile"]
        instance.address = tenant_data["address"]
        instance.status = tenant_data["status"]
        instance.updated = updated
        instance.updated_name = updated.nickname if updated else ""
        instance.save()

        super_tenant_user = (
            TenantUser.objects.all_tenants()
            .filter(
                tenant_id=instance.id,
                username=TenantConstant.SUPER_USERNAME,
            )
            .first()
        )
        if super_tenant_user:
            super_tenant_user.name = tenant_data["contact_name"]
            super_tenant_user.email = tenant_data["contact_email"]
            super_tenant_user.mobile = tenant_data["contact_mobile"]
            super_tenant_user.save(
                update_fields=(
                    "name",
                    "email",
                    "mobile",
                    "updated_at",
                )
            )

        return instance

    @classmethod
    def soft_delete(cls, instance: Tenant, deleted: Optional[SystemUser] = None):
        instance.is_delete = True
        instance.updated = deleted
        instance.updated_name = deleted.nickname if deleted else ""
        instance.save(
            update_fields=(
                "is_delete",
                "updated",
                "updated_name",
                "updated_at",
            )
        )
