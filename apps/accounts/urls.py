from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import apis

router = SimpleRouter()

router.register("system-users", apis.SystemUserViewSet, basename="system-users")
router.register(
    "system-user", apis.SystemUserOperationViewSet, basename="system-user-operation"
)
router.register("department", apis.DepartmentViewSet, basename="department")
router.register("permission", apis.PermissionViewSet, basename="permission")
router.register("role", apis.RoleViewSet, basename="role")

urlpatterns = [
    path("", include(router.urls)),
]
