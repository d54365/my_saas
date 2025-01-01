from common.permissions import HasPermission
from common.services.jwt import SystemUserJWTAuthentication
from common.views import BaseModelViewSet

from .filters import TenantFilter
from .serializers import (
    TenantInputSerializer,
    TenantOutputSerializer,
)
from .services.tenant import TenantService


class TenantViewSet(BaseModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = TenantService
    queryset = service.all()
    serializer_class = TenantOutputSerializer
    serializer_action_classes = {
        "create": TenantInputSerializer,
        "update": TenantInputSerializer,
    }
    filterset_class = TenantFilter

    action_permissions = {
        "list": "system:tenant:list",
        "retrieve": "system:tenant:retrieve",
        "create": "system:tenant:create",
        "update": "system:tenant:update",
        "destroy": "system:tenant:delete",
    }
