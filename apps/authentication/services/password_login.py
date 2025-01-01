from accounts.services.system_user import SystemUserService
from common.exceptions import ApplicationException
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .base_login import BaseLoginService
from .login_attempt_manager import LoginAttemptManager


class PasswordLoginService(BaseLoginService):
    def authenticate(self, request, username, password):
        login_manager = LoginAttemptManager(
            identifier=username,
            max_attempts=settings.LOGIN_MAX_ATTEMPTS,
            lockout_time=settings.LOGIN_LOCKOUT_TIME,
        )

        # 检查用户是否已被锁定
        if login_manager.is_locked():
            raise ApplicationException(
                _("登录失败次数过多, 您的账号已被锁定, 请稍后再试")
            )

        user = SystemUserService.get_by_username(username)
        if not user:
            # 记录失败尝试
            login_manager.record_failed_attempts()
            raise ApplicationException(_("用户名或密码错误"))

        if not user.check_password(password):
            # 记录失败尝试
            login_manager.record_failed_attempts()
            raise ApplicationException(_("用户名或密码错误"))

        self.check_user(user, login_manager)

        # 登录成功, 重置失败次数
        login_manager.reset_attempts()

        return self.post_authenticate(request, user)
