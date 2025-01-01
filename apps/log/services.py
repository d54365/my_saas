from typing import Dict, List

from django.core.cache import cache

from .constants import LogConstant
from .models import RequestLog


class RequestLogService:
    @staticmethod
    def create_batch(logs: List[Dict]):
        """
        批量写入日志
        :param logs: 日志数据列表
        """
        log_objects = [RequestLog(**log) for log in logs]
        return RequestLog.objects.bulk_create(log_objects)

    @staticmethod
    def write_to_queue(log_data):
        """写入队列"""
        cache.lpush(LogConstant.LOG_BATCH_LIST_KEY, log_data)

    @staticmethod
    def all():
        return RequestLog.objects.all().order_by("-created_at")
