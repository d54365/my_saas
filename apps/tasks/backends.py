from celery.backends.base import BaseBackend
from django.utils import timezone

from .services import CeleryTaskResultService


class CeleryResultBackend(BaseBackend):
    def store_result(
        self, task_id, result, status, traceback=None, request=None, **kwargs
    ):
        if status not in ["SUCCESS", "FAILURE", "RETRY", "REVOKED"]:
            return

        kwargs_data = getattr(request, "kwargs", {})
        if not kwargs_data.get("log_result", True):
            return

        """将任务结果存储到自定义的数据库模型中"""
        if isinstance(result, Exception):
            result = str(result)  # 将异常转换为字符串

        result = self.encode(result)

        if traceback is None:
            traceback = self.encode(traceback)

        task_data = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "traceback": traceback,
            "task_name": request.task if request else self.encode(request),
            "created_at": timezone.now(),
        }

        CeleryTaskResultService.write_to_queue(task_data)

        return True
