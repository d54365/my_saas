from functools import wraps

from accounts.services.permission import PermissionService
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        action_permissions = getattr(view, "action_permissions", {})
        required_permission = action_permissions.get(view.action, None)

        if not required_permission:
            # 未配置权限要求, 默认通过
            return True

        if user.is_super:
            # 超级管理员拥有所有权限
            return True

        user_permissions = PermissionService.get_user_permissions(user)

        if required_permission not in user_permissions:
            raise PermissionDenied()

        return True


def require_permission(permission_code):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied()

            if user.is_super:
                # 超级管理员拥有所有权限
                return func(self, request, *args, **kwargs)

            user_permissions = PermissionService.get_user_permissions(user)

            if permission_code not in user_permissions:
                raise PermissionDenied()

            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator
