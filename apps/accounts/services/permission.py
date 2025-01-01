from typing import List, Optional

from accounts.models import Permission, Role, SystemUser
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone


class PermissionService:
    PERMISSIONS_CACHE_KEY_TEMPLATE = "accounts:permissions:user:{user_id}"
    PERMISSIONS_CACHE_TIMEOUT = 60 * 60

    @staticmethod
    def get_by_id(permission_id: int) -> Optional[Permission]:
        try:
            return Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return None

    @staticmethod
    def get_by_id_list(permission_id_list: List[int]) -> QuerySet[Permission]:
        return Permission.objects.filter(id__in=permission_id_list).order_by("id")

    @staticmethod
    def code_exists(code: str, instance: Optional[Permission] = None) -> bool:
        queryset = Permission.objects.filter(code=code)
        if instance:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @staticmethod
    def all() -> QuerySet:
        return Permission.objects.all().order_by("-id")

    @staticmethod
    def tree() -> List[dict]:
        permissions = Permission.objects.all().order_by("id")
        permission_dict = {}
        tree = []

        # 初始化字典结构，确保只返回序列化数据
        for perm in permissions:
            permission_dict[perm.id] = {
                "id": perm.id,
                "code": perm.code,
                "name": perm.name,
                "description": perm.description,
                "is_category": perm.is_category,
                "children": [],
            }

        # 构建树形结构
        for perm in permissions:
            if perm.parent_id:
                parent = permission_dict.get(perm.parent_id)
                if parent:
                    parent["children"].append(permission_dict[perm.id])
            else:
                tree.append(permission_dict[perm.id])

        return tree

    @staticmethod
    def create(
        permission_data: dict, created: Optional[SystemUser] = None
    ) -> Permission:
        return Permission.objects.create(
            code=permission_data["code"],
            name=permission_data["name"],
            description=permission_data["description"],
            parent=permission_data["parent"],
            is_category=permission_data["is_category"],
            created=created,
            created_name=created.nickname if created else "",
        )

    @staticmethod
    def update(
        instance: Permission,
        permission_data: dict,
        updated: Optional[SystemUser] = None,
    ) -> Permission:
        instance.code = permission_data["code"]
        instance.name = permission_data["name"]
        instance.description = permission_data["description"]
        instance.parent = permission_data["parent"]
        instance.is_category = permission_data["is_category"]
        instance.updated = updated
        instance.updated_name = updated.nickname if updated else ""
        instance.save()
        return instance

    @classmethod
    @transaction.atomic
    def soft_delete(cls, permission: Permission, deleted: Optional[SystemUser] = None):
        """
        批量删除权限及其子权限
        """
        # 找到所有子权限，包括自身
        permissions_to_delete = cls._get_all_descendants(permission)

        # 批量更新子权限的状态
        now = timezone.now()
        permissions_to_delete.update(
            is_delete=True,
            updated=deleted,
            updated_name=deleted.nickname if deleted else "",
            updated_at=now,
        )

        related_roles = Role.objects.filter(permission__in=permissions_to_delete)
        related_users = SystemUser.objects.filter(role__in=related_roles)
        for user in related_users:
            cls.clear_user_permissions_cache(user.id)

    @staticmethod
    def _get_all_descendants(permission: Permission) -> QuerySet:
        """
        获取权限及其所有子权限
        """
        return Permission.objects.filter(
            Q(id=permission.id) | Q(parent_id=permission.id)
        )

    @classmethod
    def get_user_permissions(cls, user):
        """
        获取用户所有的权限编码
        """
        key = cls.PERMISSIONS_CACHE_KEY_TEMPLATE.format(user_id=user.id)
        cached_permission = cache.get(key)

        if cached_permission is not None:
            return cached_permission

        permissions = list(
            Permission.objects.filter(
                accounts_role_permission__accounts_system_user_role=user,
                is_delete=False,
            ).values_list("code", flat=True)
        )

        cache.set(key, permissions, cls.PERMISSIONS_CACHE_TIMEOUT)

        return permissions

    @classmethod
    def clear_user_permissions_cache(cls, user_id: int):
        key = cls.PERMISSIONS_CACHE_KEY_TEMPLATE.format(user_id=user_id)
        cache.delete(key)
