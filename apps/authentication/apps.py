from common.ip2location import IP2LocationBackend
from django.apps import AppConfig
from django.conf import settings


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        # 初始化 IP2Location 数据库
        if hasattr(settings, "IP2LOCATION_DATABASE_PATH"):
            IP2LocationBackend.initialize(settings.IP2LOCATION_DATABASE_PATH)
