from accounts.services.system_user import SystemUserService
from common.exceptions import ApplicationException
from common.services.sms import SMSService
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .base_login import BaseLoginService
from .login_attempt_manager import LoginAttemptManager


class SMSLoginService(BaseLoginService):
    def authenticate(self, request, mobile, code):
        login_manager = LoginAttemptManager(
            identifier=mobile,
            max_attempts=settings.LOGIN_MAX_ATTEMPTS,
            lockout_time=settings.LOGIN_LOCKOUT_TIME,
        )

        if not SMSService.verify_login_code(mobile, code):
            login_manager.record_failed_attempts()
            raise ApplicationException(_("验证码不正确或已过期"))

        user = SystemUserService.get_by_mobile(mobile)
        if not user:
            login_manager.record_failed_attempts()
            raise ApplicationException(_("用户不存在"))

        self.check_user(user, login_manager)

        login_manager.reset_attempts()

        SMSService.delete_login_code(mobile)

        return self.post_authenticate(request, user, self.LOGIN_TYPE_SMS)
