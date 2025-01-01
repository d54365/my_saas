from typing import List, Optional

from accounts.models import Role, SystemUser
from accounts.services.permission import PermissionService
from django.db import transaction
from django.db.models import QuerySet


class RoleService:
    @staticmethod
    def get_by_id(role_id: int) -> Optional[Role]:
        try:
            return Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_by_id_list(role_id_list: List[int]) -> QuerySet[Role]:
        return Role.objects.filter(id__in=role_id_list)

    @staticmethod
    def name_exists(name: str, instance: Optional[Role] = None) -> bool:
        queryset = Role.objects.filter(name=name)
        if instance:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @staticmethod
    def all() -> QuerySet:
        return Role.objects.all().order_by("-id")

    @staticmethod
    @transaction.atomic
    def create(
        role_data: dict,
        created: Optional[SystemUser] = None,
    ) -> Role:
        role = Role.objects.create(
            name=role_data["name"],
            description=role_data["description"],
            created=created,
            created_name=created.nickname if created else "",
        )
        if role_data["permissions"]:
            role.permission.add(*role_data["permissions"])
        return role

    @staticmethod
    @transaction.atomic
    def update(
        instance: Role, role_data: dict, updated: Optional[SystemUser] = None
    ) -> Role:
        instance.name = role_data["name"]
        instance.description = role_data["description"]
        instance.updated = updated
        instance.updated_name = updated.nickname if updated else ""
        instance.save()

        instance.permission.clear()
        if role_data["permissions"]:
            instance.permission.add(*role_data["permissions"])

        # 清除相关用户的权限缓存
        related_users = instance.accounts_system_user_role.all()
        for user in related_users:
            PermissionService.clear_user_permissions_cache(user.id)

        return instance

    @classmethod
    def soft_delete(cls, instance: Role, deleted: Optional[SystemUser] = None):
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

        # 清除相关用户的权限缓存
        related_users = instance.accounts_system_user_role.all()
        for user in related_users:
            PermissionService.clear_user_permissions_cache(user.id)
