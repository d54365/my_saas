from common.permissions import HasPermission
from common.services.jwt import SystemUserJWTAuthentication
from common.views import BaseReadOnlyModelViewSet

from .filters import CeleryTaskResultFilter
from .serializers import (
    CeleryTaskResultOutputSerializer,
    PeriodicTaskOutputSerializer,
)
from .services import CeleryTaskResultService, PeriodicTaskService


class PeriodicTaskViewSet(BaseReadOnlyModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = PeriodicTaskService
    queryset = service.all()
    serializer_class = PeriodicTaskOutputSerializer

    action_permissions = {
        "list": "tasks:periodic_task:list",
        "retrieve": "tasks:periodic_task:retrieve",
    }


class CeleryTaskResultViewSet(BaseReadOnlyModelViewSet):
    authentication_classes = (SystemUserJWTAuthentication,)
    permission_classes = (HasPermission,)
    service = CeleryTaskResultService
    queryset = service.all()
    serializer_class = CeleryTaskResultOutputSerializer
    filterset_class = CeleryTaskResultFilter

    action_permissions = {
        "list": "tasks:periodic_task_result:list",
        "retrieve": "tasks:periodic_task_result:retrieve",
    }
