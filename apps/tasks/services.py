from django.core.cache import cache
from django.db import transaction
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .constants import TasksConstant
from .models import CeleryTaskResult


class CrontabScheduleService:
    @staticmethod
    def get_or_create(
        minute: str = "*",
        hour: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*",
        day_of_week: str = "*",
    ):
        return CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )


class PeriodicTaskService:
    @staticmethod
    def all():
        return PeriodicTask.objects.filter(enabled=True).order_by("-id")

    @staticmethod
    def get_by_pk(pk: int):
        try:
            instance = PeriodicTask.objects.get(id=pk, enabled=True)
        except PeriodicTask.DoesNotExist:
            return None
        return instance

    @staticmethod
    def get_by_name(task_name: str):
        try:
            instance = PeriodicTask.objects.get(name=task_name, enabled=True)
        except PeriodicTask.DoesNotExist:
            return None
        return instance

    @staticmethod
    def create(name: str, task: str, crontab, kwargs: str):
        return PeriodicTask.objects.create(
            name=name,
            task=task,
            crontab=crontab,
            enabled=True,
            kwargs=kwargs,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: PeriodicTask, validated_data):
        minute, hour, day_of_month, month_of_year, day_of_week = validated_data[
            "cron_expression"
        ]
        crontab, created = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )
        instance.crontab = crontab
        instance.expires = validated_data["expires"]
        instance.start_time = validated_data["start_time"]
        instance.description = validated_data["description"]
        instance.save()
        return instance

    @staticmethod
    def delete(instance: PeriodicTask):
        instance.enabled = False
        instance.save()

    @staticmethod
    def get_results(instance: PeriodicTask):
        return CeleryTaskResult.objects.filter(
            task_name=instance.name,
        ).order_by("-id")


class CeleryTaskResultService:
    @staticmethod
    def create_batch(task_datas):
        """批量写入"""
        task_results = [CeleryTaskResult(**task_data) for task_data in task_datas]
        return CeleryTaskResult.objects.bulk_create(task_results)

    @staticmethod
    def write_to_queue(task_data):
        """写入队列"""
        cache.lpush(TasksConstant.CELERY_TASK_RESULT_KEY, task_data)

    @staticmethod
    def all():
        return CeleryTaskResult.objects.all().order_by("-created_at")
