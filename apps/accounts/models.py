from common.db.models import BaseModel, ForeignKey, ManyToManyField
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class SystemUser(AbstractBaseUser, BaseModel):
    MFA_TYPE_NONE = 0
    MFA_TYPE_SMS = 1
    MFA_TYPE_TOTP = 2
    MFA_TYPE_CHOICES = (
        (MFA_TYPE_NONE, "未启用"),
        (MFA_TYPE_SMS, "短信验证"),
        (MFA_TYPE_TOTP, "TOTP 验证"),
    )

    username = models.CharField(max_length=32, verbose_name="用户名", unique=True)
    password = models.CharField(max_length=128, verbose_name="密码")
    nickname = models.CharField(max_length=32, verbose_name="昵称", db_index=True)
    email = models.CharField(max_length=64, verbose_name="邮箱", unique=True)
    mobile = models.CharField(max_length=32, verbose_name="手机号码", unique=True)
    avatar = models.CharField(max_length=128, verbose_name="头像", default="")
    created = ForeignKey(
        "self", verbose_name="创建人", related_name="accounts_system_user_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        "self", verbose_name="上次修改人", related_name="accounts_system_user_updated"
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )
    last_login_at = models.DateTimeField(verbose_name="上次登陆时间", null=True)
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    is_super = models.BooleanField(default=False, verbose_name="是否是管理员")
    mfa_type = models.PositiveSmallIntegerField(
        choices=MFA_TYPE_CHOICES, default=MFA_TYPE_NONE, verbose_name="MFA类型"
    )
    totp_key = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="TOTP 密钥"
    )
    department = ForeignKey(
        "Department", related_name="accounts_system_user_department"
    )
    role = ManyToManyField("Role", related_name="accounts_system_user_role")

    REQUIRED_FIELDS = ["nickname", "email", "mobile", "password"]
    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = "系统用户"


class Department(BaseModel):
    name = models.CharField(max_length=255, verbose_name="部门名称")
    parent = ForeignKey(
        "self", verbose_name="上级部门", related_name="accounts_department_parent"
    )
    path = models.CharField(max_length=512, db_index=True, verbose_name="层级路径")
    created = ForeignKey(
        SystemUser, verbose_name="创建人", related_name="accounts_department_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        SystemUser,
        verbose_name="上次修改人",
        related_name="accounts_department_updated",
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )

    def __str__(self):
        return self.name


class Permission(BaseModel):
    code = models.CharField(max_length=64, db_index=True, verbose_name="权限编码")
    name = models.CharField(max_length=128, verbose_name="权限名称")
    description = models.CharField(max_length=256, verbose_name="权限描述", default="")
    parent = ForeignKey(
        "self", verbose_name="上级权限", related_name="accounts_permission_parent"
    )
    is_category = models.BooleanField(default=False, verbose_name="是否为分类节点")
    created = ForeignKey(
        SystemUser, verbose_name="创建人", related_name="accounts_permission_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        SystemUser,
        verbose_name="上次修改人",
        related_name="accounts_permission_updated",
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )

    def __str__(self):
        return f"{self.name}:{self.code}"


class Role(BaseModel):
    name = models.CharField(max_length=64, verbose_name="角色名称")
    description = models.CharField(max_length=128, verbose_name="角色描述", default="")
    permission = ManyToManyField(
        Permission, verbose_name="权限", related_name="accounts_role_permission"
    )
    created = ForeignKey(
        SystemUser, verbose_name="创建人", related_name="accounts_role_created"
    )
    created_name = models.CharField(max_length=32, verbose_name="创建人姓名")
    updated = ForeignKey(
        SystemUser, verbose_name="上次修改人", related_name="accounts_role_updated"
    )
    updated_name = models.CharField(
        max_length=32, verbose_name="上次修改人姓名", default=""
    )

    def __str__(self):
        return self.name
