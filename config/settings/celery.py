import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from kombu import Exchange, Queue

# 设置默认的 Django 设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("my_saas")

# celery -A config worker -Q default -l info -c 1
# celery -A config beat -l info

app.conf.task_queues = (Queue("default", Exchange("default"), routing_key="default"),)

app.conf.task_routes = {}

app.conf.update(
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# 使用 Django 的设置文件进行配置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 配置定时任务
app.conf.beat_schedule = {
    "clean-expired-sessions-task": {
        "task": "clean_expiration_access_token",
        "schedule": crontab(minute="0"),  # 每小时的整点执行
    },
    "clean-expiration-refresh-token": {
        "task": "clean_expiration_refresh_token",
        "schedule": crontab(hour="*/8", minute="0"),  # 每 8 小时的整点执行
    },
    "clean-expired-sessions": {
        "task": "clean_expired_sessions",
        "schedule": crontab(minute="0"),  # 每小时的整点执行
    },
    "process_celery_task_results": {
        "task": "process_celery_task_results",
        "schedule": crontab(minute="10,20,30,40,50,0"),  # 每 10 分钟整点执行一次
    },
    "process_request_log": {
        "task": "process_request_log",
        "schedule": crontab(minute="*/5"),  # 每 5 分钟执行一次
    },
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
