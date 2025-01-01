from common.idworker import id_worker
from common.middlewares.tenant import get_current_tenant
from django.core.exceptions import ImproperlyConfigured
from django.db import models


class ForeignKey(models.ForeignKey):
    def __init__(
        self,
        to,
        on_delete=models.SET_NULL,
        related_name=None,
        related_query_name=None,
        limit_choices_to=None,
        parent_link=False,
        to_field=None,
        db_constraint=False,
        **kwargs,
    ):
        kwargs["null"] = True
        super().__init__(
            to,
            on_delete,
            related_name,
            related_query_name,
            limit_choices_to,
            parent_link,
            to_field,
            db_constraint,
            **kwargs,
        )


class ManyToManyField(models.ManyToManyField):
    def __init__(
        self,
        to,
        related_name=None,
        related_query_name=None,
        limit_choices_to=None,
        symmetrical=None,
        through=None,
        through_fields=None,
        db_constraint=False,
        db_table=None,
        swappable=True,
        **kwargs,
    ):
        super().__init__(
            to,
            related_name,
            related_query_name,
            limit_choices_to,
            symmetrical,
            through,
            through_fields,
            db_constraint,
            db_table,
            swappable,
            **kwargs,
        )


class BaseManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._include_deleted_filtering = False

    def with_deleted_filtering(self, enable=True):
        self._include_deleted_filtering = not enable
        return self

    def get_queryset(self):
        if self._include_deleted_filtering:
            return super().get_queryset()

        return super().get_queryset().filter(is_delete=False)


def generate_id():
    # 直接在 fields 上写 default=id_worker.get_id会导致每次 makemigrations 都显示进行表改动
    # 注意: ManyToManyField 生成的表的主键还是自增 ID
    return id_worker.get_id()


class BaseModel(models.Model):
    id = models.BigIntegerField(primary_key=True, default=generate_id)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    objects = BaseManager()

    class Meta:
        abstract = True


class TenantManager(BaseManager):
    def get_queryset(self):
        print(self)
        tenant_id = get_current_tenant()
        if tenant_id is None:
            raise ImproperlyConfigured("tenant_id cannot be None")
        return super().get_queryset().filter(tenant_id=tenant_id)

    def all_tenants(self):
        return super().get_queryset()


class TenantBaseModel(BaseModel):
    tenant_id = models.BigIntegerField(db_index=True, verbose_name="租户 ID")

    objects = TenantManager()

    class Meta:
        abstract = True
