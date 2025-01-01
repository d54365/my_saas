from celery import shared_task
from django.core.cache import cache

from .constants import TasksConstant
from .services import CeleryTaskResultService


@shared_task(
    name="process_celery_task_results", bind=True, max_retries=3, default_retry_delay=10
)
def process_celery_task_results(self, *args, **kwargs):
    task_data = kwargs.get("task_data") or self.request.kwargs.get("task_data")
    try:
        if task_data:
            CeleryTaskResultService.create_batch(task_data)
        else:
            task_data = []
            for _ in range(TasksConstant.BATCH_PROCESS_SIZE):
                value = cache.rpop(TasksConstant.CELERY_TASK_RESULT_KEY)
                if not value:
                    break
                task_data.append(value)

            if not task_data:
                return

            CeleryTaskResultService.create_batch(task_data)
    except Exception as e:
        print(f"process_celery_task_results failed: {e}")
        # 重试时从上下文中自动传递参数
        self.retry(exc=e, task_data=task_data)
