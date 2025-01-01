from clickhouse_backend import models as clickhouse_models
from clickhouse_backend.models import ClickhouseModel


class CeleryTaskResult(ClickhouseModel):
    task_id = clickhouse_models.StringField(verbose_name="任务 ID")
    task_name = clickhouse_models.StringField(verbose_name="任务名称")
    status = clickhouse_models.StringField(verbose_name="任务状态")
    result = clickhouse_models.StringField(verbose_name="任务结果")
    traceback = clickhouse_models.StringField(default="", verbose_name="异常信息")
    created_at = clickhouse_models.DateTimeField()

    class Meta:
        verbose_name = "异步任务结果"
        engine = clickhouse_models.MergeTree(
            order_by=("created_at",),
            partition_by=clickhouse_models.toYYYYMM("created_at"),
        )
        indexes = [
            clickhouse_models.Index(
                fields=["task_name"],
                name="idx_task_name",
                type=clickhouse_models.BloomFilter(0.001),
                granularity=64,
            ),
            clickhouse_models.Index(
                fields=["status"],
                name="idx_status",
                type=clickhouse_models.BloomFilter(0.001),
                granularity=64,
            ),
        ]
