from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .apis import CeleryTaskResultViewSet, PeriodicTaskViewSet

router = SimpleRouter()

router.register("periodic", PeriodicTaskViewSet, basename="task-periodic-task")
router.register("result", CeleryTaskResultViewSet, basename="task-celery-task-result")

urlpatterns = [
    path("", include(router.urls)),
]
