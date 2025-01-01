from accounts.models import SystemUser
from common.db.models import BaseModel, ForeignKey, TenantBaseModel
from django.db import models


class Tenant(BaseModel):
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUS_SUSPENDED = 2
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "激活"),
        (STATUS_INACTIVE, "未激活"),
        (STATUS_SUSPENDED, "已暂停"),
    )

    name = models.CharField(max_length=255, db_index=True, verbose_name="租户名称")
    contact_name = models.CharField(max_length=64, verbose_name="联系人姓名")
    contact_email = models.CharField(max_length=128, verbose_name="联系人邮箱")
    contact_mobile = models.CharField(max_length=32, verbose_name="联系人电话")
    address = models.TextField(max_length=255, default="", verbose_name="租户地址")
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, verbose_name="租户状态"
    )
    created = ForeignKey(
        SystemUser, verbose_name="创建人", related_name="tenant_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        SystemUser, verbose_name="上次修改人", related_name="tenant_updated"
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )

    def __str__(self):
        return self.name


class TenantUser(TenantBaseModel):
    username = models.CharField(max_length=64, db_index=True, verbose_name="用户名")
    password = models.CharField(max_length=128, verbose_name="密码")
    name = models.CharField(max_length=64, verbose_name="姓名")
    email = models.CharField(max_length=128, db_index=True, verbose_name="邮箱地址")
    mobile = models.CharField(max_length=32, db_index=True, verbose_name="电话")
    is_super = models.BooleanField(default=False, verbose_name="是否是租户管理员")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    last_login_at = models.DateTimeField(verbose_name="上次登陆时间", null=True)
    created = ForeignKey(
        "self", verbose_name="创建人", related_name="tenant_user_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        "self", verbose_name="上次修改人", related_name="tenant_user_updated"
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )

    def __str__(self):
        return self.username
