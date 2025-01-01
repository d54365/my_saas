from clickhouse_backend import models as clickhouse_models
from clickhouse_backend.models import ClickhouseModel


class RequestLog(ClickhouseModel):
    created_at = clickhouse_models.DateTimeField(verbose_name="请求时间")
    api_path = clickhouse_models.StringField(verbose_name="接口地址")
    client_ip = clickhouse_models.StringField(verbose_name="客户端 IP 地址")
    user_id = clickhouse_models.StringField(default="", verbose_name="用户标识")
    user_agent = clickhouse_models.StringField(verbose_name="User-Agent 信息")
    referer = clickhouse_models.StringField(default="", verbose_name="Referer 来源")
    origin = clickhouse_models.StringField(default="", verbose_name="Origin")
    status_code = clickhouse_models.UInt16Field(verbose_name="状态码")
    host = clickhouse_models.StringField(verbose_name="主机地址")
    duration = clickhouse_models.Float64Field(verbose_name="请求耗时")
    country = clickhouse_models.StringField(default="", verbose_name="国家")
    region = clickhouse_models.StringField(default="", verbose_name="区域")
    city = clickhouse_models.StringField(default="", verbose_name="城市")
    time_zone = clickhouse_models.StringField(default="", verbose_name="时区")
    device_brand = clickhouse_models.StringField(default="", verbose_name="设备品牌")
    device_model = clickhouse_models.StringField(default="", verbose_name="设备型号")
    device_family = clickhouse_models.StringField(default="")
    device_type = clickhouse_models.StringField(default="", verbose_name="设备类型")
    os_family = clickhouse_models.StringField(default="", verbose_name="操作系统名称")
    os_version = clickhouse_models.StringField(default="", verbose_name="操作系统版本")
    browser_family = clickhouse_models.StringField(
        default="", verbose_name="浏览器名称"
    )
    browser_version = clickhouse_models.StringField(
        default="", verbose_name="浏览器版本"
    )
    accept_language = clickhouse_models.StringField(
        default="", verbose_name="用户语言偏好"
    )
    request_id = clickhouse_models.StringField(default="", verbose_name="请求标识")
    query_params = clickhouse_models.StringField(default="", verbose_name="query 参数")
    body_params = clickhouse_models.StringField(default="", verbose_name="body 参数")
    method = clickhouse_models.StringField(
        default="", verbose_name="请求方式, GET/POST/PUT/DELETE"
    )
    tenant_id = clickhouse_models.StringField(default="", verbose_name="租户 ID")

    class Meta:
        verbose_name = "请求日志"
        engine = clickhouse_models.MergeTree(
            order_by=("created_at",),
            partition_by=clickhouse_models.toYYYYMM("created_at"),
        )
        indexes = [
            clickhouse_models.Index(
                fields=["api_path"],
                name="idx_api_path",
                type=clickhouse_models.BloomFilter(0.001),
                granularity=64,
            ),
            clickhouse_models.Index(
                fields=["user_id"],
                name="idx_user_id",
                type=clickhouse_models.BloomFilter(0.001),
                granularity=64,
            ),
            clickhouse_models.Index(
                fields=["request_id"],
                name="idx_request_id",
                type=clickhouse_models.BloomFilter(0.001),
                granularity=64,
            ),
        ]
