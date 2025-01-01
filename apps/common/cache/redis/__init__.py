from django.core.cache import cache

from .script_manager import RedisScriptManager

script_manager = RedisScriptManager(cache)

__all__ = ("script_manager",)
