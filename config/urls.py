from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/authentication/", include("authentication.urls")),
    path("api/v1/tasks/", include("tasks.urls")),
    path("api/v1/log/", include("log.urls")),
    path("api/v1/system/", include("tenant.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
