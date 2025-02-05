from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

from .base import BaseIDWorker
from .snowflake import SnowflakeIDWorker

__all__ = ["BaseIDWorker", "SnowflakeIDWorker", "id_worker"]

id_worker = SimpleLazyObject(
    lambda: import_string(
        getattr(
            settings,
            "ID_WORKER",
            "common.idworker.snowflake.snowflake_worker",
        )
    )
)
