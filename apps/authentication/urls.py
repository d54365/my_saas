from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .apis import SystemUserAuthenticationViewSet

router = SimpleRouter()

router.register("system-user", SystemUserAuthenticationViewSet, basename="system-user")

urlpatterns = [
    path("", include(router.urls)),
]
