from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import apis

router = SimpleRouter()

router.register("tenant", apis.TenantViewSet, basename="system-tenant")

urlpatterns = [
    path("", include(router.urls)),
]
