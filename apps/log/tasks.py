from celery import shared_task
from django.core.cache import cache

from .constants import LogConstant
from .services import RequestLogService


@shared_task(
    name="process_request_log", bind=True, max_retries=3, default_retry_delay=10
)
def process_request_log(self, *args, **kwargs):
    logs = kwargs.get("logs") or self.request.kwargs.get("task_data")
    try:
        if logs:
            RequestLogService.create_batch(logs)
        else:
            task_data = []
            for _ in range(LogConstant.BATCH_PROCESS_SIZE):
                value = cache.rpop(LogConstant.LOG_BATCH_LIST_KEY)
                if not value:
                    break
                task_data.append(value)

            if not task_data:
                return

            RequestLogService.create_batch(task_data)
    except Exception as e:
        print(f"process_request_log failed: {e}")
        # 重试时从上下文中自动传递参数
        self.retry(exc=e, logs=logs)
