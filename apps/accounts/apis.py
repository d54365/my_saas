from accounts.services.system_user import (
    SystemUserService,
)
from common.permissions import HasPermission
from common.services.jwt import SystemUserJWTAuthentication
from common.views import BaseModelViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import (
    DepartmentFilter,
    PermissionFilter,
    RoleFilter,
    SystemUserFilter,
)
from .models import SystemUser
from .serializers import (
    ActiveSessionsOutputSerializer,
    DepartmentInputSerializer,
    DepartmentOutputSerializer,
    PermissionInputSerializer,
    PermissionOutputSerializer,
    RoleDetailOutputSerializer,
    RoleInputSerializer,
    RoleOutputSerializer,
    SystemUserChangeMFATypeInputSerializer,
    SystemUserCreateInputSerializer,
    SystemUserInfoOutputSerializer,
    SystemUserLogoutSessionInputSerializer,
    SystemUserOutputSerializer,
    SystemUserUpdateInputSerializer,
)
from .services.department import DepartmentService
from .services.permission import PermissionService
from .services.role import RoleService


class SystemUserViewSet(BaseModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = SystemUserService
    queryset = service.all().prefetch_related("department", "role")
    serializer_class = SystemUserOutputSerializer
    serializer_action_classes = {
        "create": SystemUserCreateInputSerializer,
        "update": SystemUserUpdateInputSerializer,
    }
    filterset_class = SystemUserFilter

    action_permissions = {
        "list": "accounts:system_user:list",
        "retrieve": "accounts:system_user:retrieve",
        "create": "accounts:system_user:create",
        "update": "accounts:system_user:update",
        "destroy": "accounts:system_user:delete",
    }


class SystemUserOperationViewSet(viewsets.ViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)

    @action(methods=["GET"], detail=False, url_path="info")
    def info(self, request):
        serializer = SystemUserInfoOutputSerializer(request.user)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path="mfa-type")
    def change_mfa_type(self, request):
        serializer = SystemUserChangeMFATypeInputSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        mfa_type = serializer.validated_data["mfa_type"]

        if request.user.mfa_type == mfa_type:
            return Response()

        if mfa_type == SystemUser.MFA_TYPE_NONE:
            SystemUserService.disable_mfa(request.user)
        else:
            SystemUserService.enable_mfa(request.user, mfa_type)

        return Response()

    @action(
        methods=["GET"],
        detail=False,
        url_path="active-sessions",
    )
    def active_sessions(self, request):
        return Response(
            ActiveSessionsOutputSerializer(
                SystemUserService.get_active_sessions(request.user.id),
                many=True,
            ).data,
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="logout-session",
    )
    def logout_session(self, request):
        user_id = request.user.id

        serializer = SystemUserLogoutSessionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.validated_data["device_id"]

        SystemUserService.logout_session(user_id, device_id)

        return Response()


class DepartmentViewSet(BaseModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = DepartmentService
    queryset = service.all()
    serializer_class = DepartmentOutputSerializer
    serializer_action_classes = {
        "create": DepartmentInputSerializer,
        "update": DepartmentInputSerializer,
    }
    filterset_class = DepartmentFilter

    action_permissions = {
        "list": "accounts:department:list",
        "retrieve": "accounts:department:retrieve",
        "create": "accounts:department:create",
        "update": "accounts:department:update",
        "destroy": "accounts:department:delete",
    }

    def list(self, request, *args, **kwargs):
        if request.query_params:
            # 平铺返回
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        # 返回树形结
        return Response(data=self.service.get_tree_cached())

    @action(methods=["GET"], detail=False, url_path="tree", permission_classes=())
    def tree(self, request):
        return Response(data=self.service.get_tree_cached())


class PermissionViewSet(BaseModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = PermissionService
    queryset = service.all()
    serializer_class = PermissionOutputSerializer
    serializer_action_classes = {
        "create": PermissionInputSerializer,
        "update": PermissionInputSerializer,
    }
    filterset_class = PermissionFilter

    action_permissions = {
        "list": "accounts:permission:list",
        "retrieve": "accounts:permission:retrieve",
        "create": "accounts:permission:create",
        "update": "accounts:permission:update",
        "destroy": "accounts:permission:delete",
    }

    def list(self, request, *args, **kwargs):
        if request.query_params:
            # 平铺返回
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        # 返回树形结
        return Response(data=self.service.tree())

    @action(methods=["GET"], detail=False, url_path="tree", permission_classes=())
    def tree(self, request):
        return Response(data=self.service.tree())


class RoleViewSet(BaseModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = RoleService
    queryset = service.all()
    serializer_class = RoleOutputSerializer
    serializer_action_classes = {
        "create": RoleInputSerializer,
        "update": RoleInputSerializer,
        "retrieve": RoleDetailOutputSerializer,
    }
    filterset_class = RoleFilter

    action_permissions = {
        "list": "accounts:role:list",
        "retrieve": "accounts:role:retrieve",
        "create": "accounts:role:create",
        "update": "accounts:role:update",
        "destroy": "accounts:role:delete",
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            return queryset.prefetch_related("permission")
        return queryset

    @action(methods=["GET"], detail=False, url_path="info", permission_classes=())
    def info(self, request):
        queryset = self.get_queryset().order_by("name")
        return Response(
            data=(
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                }
                for role in queryset
            )
        )
