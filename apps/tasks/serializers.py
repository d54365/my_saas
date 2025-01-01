from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from rest_framework import serializers

from .models import CeleryTaskResult


class CrontabScheduleOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = (
            "minute",
            "hour",
            "day_of_week",
            "day_of_month",
            "month_of_year",
        )


class PeriodicTaskOutputSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleOutputSerializer(read_only=True)

    class Meta:
        model = PeriodicTask
        fields = (
            "id",
            "name",
            "task",
            "crontab",
            "args",
            "kwargs",
            "start_time",
            "last_run_at",
            "total_run_count",
            "date_changed",
            "description",
            "expires",
        )


class PeriodicTaskUpdateInputSerializer(serializers.Serializer):
    cron_expression = serializers.CharField(write_only=True)
    expires = serializers.DateTimeField(required=False, allow_null=True, default=None)
    start_time = serializers.DateTimeField(
        required=False, allow_null=True, default=None
    )
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=""
    )

    class Meta:
        model = PeriodicTask
        fields = ("cron_expression", "start_time", "description", "expires")

    @staticmethod
    def validate_cron_expression(value):
        try:
            minute, hour, day_of_month, month_of_year, day_of_week = value.split()
            return minute, hour, day_of_month, month_of_year, day_of_week
        except ValueError as e:
            raise serializers.ValidationError(
                "Invalid cron expression format. Expected format is '* * * * *'"
            ) from e

    @staticmethod
    def validate_start_time(value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value


class CeleryTaskResultOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CeleryTaskResult
        fields = (
            "id",
            "task_id",
            "task_name",
            "status",
            "result",
            "traceback",
            "created_at",
        )
