from django.utils.translation import gettext_lazy as _


class ValidationMessages:
    INVALID_EMAIL = _("邮箱格式错误")
    INVALID_MOBILE = _("手机号格式错误")
    INVALID_PASSWORD = _("密码需由字母、数字、特殊字符，任意2种组成，8-16位")
    EMAIL_ALREADY_USED = _("邮箱已被使用")
    MOBILE_ALREADY_USED = _("手机号已被使用")
    USERNAME_ALREADY_USED = _("用户名已被使用")
