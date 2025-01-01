from common.permissions import HasPermission
from common.services.jwt import SystemUserJWTAuthentication
from common.views import BaseReadOnlyModelViewSet

from .filters import RequestLogFilter
from .serializers import RequestLogOutputSerializer
from .services import RequestLogService


class RequestLogViewSet(BaseReadOnlyModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = RequestLogService
    queryset = service.all()
    serializer_class = RequestLogOutputSerializer
    filterset_class = RequestLogFilter

    action_permissions = {
        "list": "log:request_log:list",
        "retrieve": "log:request_log:retrieve",
    }
