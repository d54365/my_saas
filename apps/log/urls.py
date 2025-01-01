from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .apis import RequestLogViewSet

router = SimpleRouter()

router.register("request", RequestLogViewSet, basename="request")

urlpatterns = [
    path("", include(router.urls)),
]
