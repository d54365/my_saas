from datetime import datetime
from typing import Any, Optional

import pyotp
from accounts.models import SystemUser
from accounts.services.permission import PermissionService
from authentication.constants import AuthConstants
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone


class SystemUserService:
    SYSTEM_USER_KEY_TEMPLATE = "accounts:system_user:{id}"
    SYSTEM_USER_KEY_TIMEOUT = 60 * 60 * 24 * 7

    @staticmethod
    def _attribute_exists(
        attribute: str, value: Any, instance: SystemUser = None
    ) -> bool:
        queryset = SystemUser.objects.filter(**{attribute: value})
        if instance:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @classmethod
    def username_exists(cls, username: str, instance: SystemUser = None) -> bool:
        return cls._attribute_exists("username", username, instance)

    @classmethod
    def email_exists(cls, email: str, instance: SystemUser = None) -> bool:
        return cls._attribute_exists("email", email, instance)

    @classmethod
    def mobile_exists(cls, mobile: str, instance: SystemUser = None) -> bool:
        return cls._attribute_exists("mobile", mobile, instance)

    @staticmethod
    @transaction.atomic
    def create(user_data, created: SystemUser = None) -> SystemUser:
        obj = SystemUser.objects.create(
            username=user_data["username"],
            nickname=user_data["nickname"],
            email=user_data["email"],
            mobile=user_data["mobile"],
            password=make_password(user_data["password"]),
            is_active=user_data["is_active"],
            department=user_data["department"],
            created=created,
            created_name=created.nickname if created.is_authenticated else "",
        )
        if user_data["roles"]:
            obj.role.add(*user_data["roles"])
        return obj

    @classmethod
    def update(
        cls, instance: SystemUser, user_data, updated: SystemUser = None
    ) -> SystemUser:
        old_role_ids = set(instance.role.values_list("id", flat=True))

        instance.nickname = user_data["nickname"]
        instance.email = user_data["email"]
        instance.mobile = user_data["mobile"]
        instance.is_active = user_data["is_active"]
        instance.department = user_data["department"]
        instance.updated = updated
        instance.updated_name = updated.nickname if updated else ""
        instance.save()

        # 更新角色
        new_roles = user_data.get("roles", [])
        new_role_ids = {role.id for role in new_roles}
        if old_role_ids != new_role_ids:
            # 如果角色有变动，更新角色关系
            instance.role.clear()
            if new_roles:
                instance.role.add(*new_roles)

            # 清除权限缓存
            PermissionService.clear_user_permissions_cache(instance.id)

        cls.delete_cache(instance)

        return instance

    @classmethod
    @transaction.atomic
    def soft_delete(cls, user: SystemUser, deleted: SystemUser = None):
        now = timezone.now()

        user.username = f"{user.username}_del_{now.minute}{now.second}"
        if user.mobile:
            user.mobile = f"{user.mobile}_del_{now.minute}{now.second}"
        if user.email:
            user.email = f"{user.email}_del_{now.minute}{now.second}"
        user.is_delete = True
        user.updated = deleted
        user.updated_name = deleted.nickname if deleted else ""
        user.save(
            update_fields=(
                "is_delete",
                "updated",
                "updated_name",
                "updated_at",
                "username",
                "mobile",
                "email",
            )
        )

        cls.delete_cache(user)

    @staticmethod
    def all():
        return SystemUser.objects.all().order_by("-id")

    @classmethod
    def get_by_id(cls, pk: int) -> Optional[SystemUser]:
        cache_key = cls.SYSTEM_USER_KEY_TEMPLATE.format(id=pk)
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            instance = SystemUser.objects.get(id=pk)
        except SystemUser.DoesNotExist:
            return None
        cache.set(cache_key, instance, cls.SYSTEM_USER_KEY_TIMEOUT)
        return instance

    @classmethod
    def update_last_login_at(cls, user: SystemUser):
        user.last_login_at = timezone.now()
        user.save(update_fields=("last_login_at",))

        cls.delete_cache(user)

    @classmethod
    def update_password(
        cls, user: SystemUser, password: str, updated: SystemUser = None
    ):
        user.password = make_password(password)
        if updated:
            # 管理员修改
            user.updated = updated
            user.updated_name = updated.nickname
            user.save(
                update_fields=("password", "updated", "updated_name", "updated_at")
            )
        else:
            # 用户自己修改
            user.save(update_fields=("password",))

        cls.delete_cache(user)

    @staticmethod
    def get_by_username(username: str):
        try:
            user = SystemUser.objects.get(username=username)
        except SystemUser.DoesNotExist:
            return None
        return user

    @staticmethod
    def get_by_mobile(mobile: str):
        try:
            user = SystemUser.objects.get(mobile=mobile)
        except SystemUser.DoesNotExist:
            return None
        return user

    @classmethod
    def delete_cache(cls, user: SystemUser):
        cache.delete(cls.SYSTEM_USER_KEY_TEMPLATE.format(id=user.id))

    @classmethod
    def enable_mfa(cls, user: SystemUser, mfa_type) -> str:
        """启用 MFA 功能"""
        user.mfa_type = mfa_type
        if mfa_type == SystemUser.MFA_TYPE_TOTP:
            user.totp_key = pyotp.random_base32()
        else:
            user.totp_key = None
        user.save(update_fields=("mfa_type", "totp_key", "updated_at"))
        cls.delete_cache(user)
        return user.totp_key

    @classmethod
    def disable_mfa(cls, user: SystemUser):
        user.mfa_type = SystemUser.MFA_TYPE_NONE
        user.totp_key = None
        user.save(update_fields=("mfa_type", "totp_key", "updated_at"))
        cls.delete_cache(user)

    @staticmethod
    def get_active_sessions(user_id):
        user_sessions_key = AuthConstants.SYSTEM_USER_ALL_SESSIONS_TEMPLATE.format(
            user_id=user_id,
        )
        device_ids = cache.smembers(user_sessions_key)

        session_keys = [
            AuthConstants.SYSTEM_USER_DEVICE_SESSION_TEMPLATE.format(
                user_id=user_id,
                device_id=device_id,
            )
            for device_id in device_ids
        ]

        session_data = cache.get_many(session_keys)
        current_timestamp = int(datetime.utcnow().timestamp())

        sessions = []
        for data in session_data.values():
            if data:
                refresh_expired_time = data.get("refresh_expired_time")
                access_expired_time = data.get("access_expired_time")
                if (
                    refresh_expired_time and refresh_expired_time > current_timestamp
                ) or (access_expired_time and access_expired_time > current_timestamp):
                    sessions.append(
                        {
                            "device_info": data.get("device_info"),
                            "ip_address": data.get("ip_address", ""),
                            "login_at": data.get("login_at"),
                            "last_active_at": data.get("last_active_at"),
                            "country": data.get("country"),
                            "region": data.get("region"),
                            "city": data.get("city"),
                        }
                    )
        return sessions

    @staticmethod
    def logout_session(user_id, device_id):
        from common.services.jwt import SystemUserJWTAuthentication

        device_session_key = AuthConstants.SYSTEM_USER_DEVICE_SESSION_TEMPLATE.format(
            user_id=user_id,
            device_id=device_id,
        )
        user_sessions_key = AuthConstants.SYSTEM_USER_ALL_SESSIONS_TEMPLATE.format(
            user_id=user_id,
        )

        session_data = cache.get(device_session_key)
        if session_data:
            refresh = session_data["refresh"]
            refresh_expired_time = session_data["refresh_expired_time"]
            access = session_data["access"]
            access_expired_time = session_data["access_expired_time"]
            SystemUserJWTAuthentication.add_access_to_blacklist(
                access,
                access_expired_time,
            )
            SystemUserJWTAuthentication.add_refresh_to_blacklist(
                refresh,
                refresh_expired_time,
            )

        cache.delete(device_session_key)
        cache.srem(user_sessions_key, device_id)

        # 如果该用户没有活跃终端，移除其 ID
        if not cache.scard(user_sessions_key):
            cache.srem(AuthConstants.SYSTEM_USER_ACTIVE, user_id)
