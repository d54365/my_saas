from accounts.services.system_user import (
    SystemUserService,
)
from common.constants import Regex
from common.exceptions import ApplicationException
from common.validators import ValidationMessages
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import (
    Department,
    Permission,
    Role,
    SystemUser,
)
from .services.department import DepartmentService
from .services.permission import PermissionService
from .services.role import RoleService


class SystemUserOutputSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = SystemUser
        fields = (
            "id",
            "username",
            "nickname",
            "email",
            "mobile",
            "is_active",
            "is_super",
            "last_login_at",
            "avatar",
            "created_name",
            "updated_name",
            "created_at",
            "updated_at",
            "mfa_type",
            "department",
            "role",
        )

    @staticmethod
    def get_department(instance):
        return (
            {
                "id": instance.department.id,
                "name": instance.department.name,
            }
            if instance.department
            else None
        )

    @staticmethod
    def get_role(instance):
        return (
            {
                "id": role.id,
                "name": role.name,
            }
            for role in instance.role.all()
        )


class SystemUserBaseInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nickname = serializers.CharField(max_length=32)
    email = serializers.RegexField(
        regex=Regex.EMAIL,
        error_messages={"invalid": ValidationMessages.INVALID_EMAIL},
    )
    mobile = serializers.RegexField(
        regex=Regex.MOBILE,
        error_messages={"invalid": ValidationMessages.INVALID_MOBILE},
    )
    is_active = serializers.BooleanField(default=True)
    department_id = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )
    role_id_list = serializers.ListField(
        write_only=True, required=False, allow_null=True, allow_empty=True
    )

    def validate_email(self, email):
        if SystemUserService.email_exists(email, self.instance):
            raise ApplicationException(ValidationMessages.EMAIL_ALREADY_USED)
        return email

    def validate_mobile(self, mobile):
        if SystemUserService.mobile_exists(mobile, self.instance):
            raise ApplicationException(ValidationMessages.MOBILE_ALREADY_USED)
        return mobile

    def validate(self, attrs):
        department_id = attrs["department_id"]
        role_id_list = attrs["role_id_list"]
        attrs["department"] = None
        attrs["roles"] = None

        if department_id:
            department = DepartmentService.get_by_id(department_id)
            if not department:
                raise ApplicationException(_("请选择正确的部门"))
            attrs["department"] = department

        if role_id_list:
            roles = RoleService.get_by_id_list(role_id_list)
            if len(roles) != len(role_id_list):
                raise ApplicationException(_("请选择正确的角色"))
            attrs["roles"] = roles

        return attrs


class SystemUserCreateInputSerializer(SystemUserBaseInputSerializer):
    username = serializers.CharField(max_length=32)
    password = serializers.RegexField(
        regex=Regex.PASSWORD,
        write_only=True,
        error_messages={
            "invalid": ValidationMessages.INVALID_PASSWORD,
        },
    )

    @staticmethod
    def validate_username(username):
        if SystemUserService.username_exists(username):
            raise ApplicationException(ValidationMessages.USERNAME_ALREADY_USED)
        return username


class SystemUserUpdateInputSerializer(SystemUserBaseInputSerializer):
    pass


class SystemUserInfoOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUser
        fields = (
            "username",
            "nickname",
            "email",
            "mobile",
            "avatar",
            "last_login_at",
            "mfa_type",
            "totp_key",
        )


class SystemUserChangeMFATypeInputSerializer(serializers.Serializer):
    mfa_type = serializers.ChoiceField(choices=SystemUser.MFA_TYPE_CHOICES)

    def validate_mfa_type(self, mfa_type):
        request = self.context["request"]
        if mfa_type == SystemUser.MFA_TYPE_SMS and not request.user.mobile:
            raise ApplicationException(_("请选绑定手机"))
        return mfa_type


class SystemUserLogoutSessionInputSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=32)


class ActiveSessionsOutputSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False, allow_null=True)
    device_info = serializers.JSONField(required=False, allow_null=True)
    ip_address = serializers.CharField()
    login_at = serializers.DateTimeField(required=False, allow_null=True)
    last_active_at = serializers.DateTimeField(required=False, allow_null=True)
    country = serializers.CharField()
    region = serializers.CharField()
    city = serializers.CharField()


class DepartmentOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "path",
            "parent_id",
            "created_at",
            "updated_at",
            "created_name",
            "updated_name",
        )


class DepartmentInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        name = attrs["name"]
        parent_id = attrs.get("parent_id", None)

        parent = None
        if parent_id is not None:
            parent = DepartmentService.get_by_id(parent_id)
            if not parent:
                raise ApplicationException(_("上级部门不存在"))

        if DepartmentService.name_exists(name, parent, self.instance):
            raise ApplicationException(_("部门名称已存在"))

        attrs["parent"] = parent
        return attrs


class PermissionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            "id",
            "code",
            "name",
            "description",
            "parent_id",
            "is_category",
            "created_name",
            "updated_name",
            "created_at",
            "updated_at",
        )


class PermissionInputSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=64, required=False, allow_null=True, allow_blank=True, default=""
    )
    name = serializers.CharField(max_length=128)
    description = serializers.CharField(
        max_length=256, required=False, allow_null=True, allow_blank=True, default=""
    )
    parent_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    is_category = serializers.BooleanField(default=False)

    def validate(self, attrs):
        code = attrs["code"]
        parent_id = attrs["parent_id"]
        is_category = attrs["is_category"]

        if not is_category and not code:
            raise ApplicationException(_("请输入权限编码"))

        parent = None
        if parent_id:
            parent = PermissionService.get_by_id(parent_id)
            if not parent:
                raise ApplicationException(_("请选择正确的上级权限"))
            if not parent.is_category:
                raise ApplicationException(_("上级权限必须是分类节点"))

        if code:
            if PermissionService.code_exists(code, self.instance):
                raise ApplicationException(_("权限编码已被使用"))

        attrs["parent"] = parent
        return attrs


class RoleOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "created_name",
            "updated_name",
            "created_at",
            "updated_at",
        )


class RoleDetailOutputSerializer(serializers.ModelSerializer):
    permission = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "permission",
            "created_name",
            "updated_name",
            "created_at",
            "updated_at",
        )

    @staticmethod
    def get_permission(instance):
        return (permission.id for permission in instance.permission.all())


class RoleInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    description = serializers.CharField(
        max_length=256, required=False, allow_null=True, allow_blank=True, default=""
    )
    permission_id_list = serializers.ListField(
        write_only=True,
        required=False,
        allow_null=True,
        allow_empty=True,
        default=None,
    )

    def validate_name(self, name):
        if RoleService.name_exists(name, self.instance):
            raise ApplicationException(_("角色名称已被使用"))
        return name

    def validate(self, attrs):
        permission_id_list = attrs["permission_id_list"]

        permissions = None

        if permission_id_list:
            permissions = PermissionService.get_by_id_list(permission_id_list)
            if len(permissions) != len(permission_id_list):
                raise ApplicationException(_("请选择正确的权限"))

        attrs["permissions"] = permissions
        return attrs
