from accounts.models import SystemUser
from accounts.services.system_user import SystemUserService
from authentication.services.sms_code_limiter import VerificationCodeLimiter
from common.constants import Regex
from common.exceptions import ApplicationException
from common.header import HeaderUtil
from common.services.sms import SMSService
from common.validators import ValidationMessages
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import AuthConstants
from .services.mfa import MFAService


class PasswordLoginInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class SMSLoginInputSerializer(serializers.Serializer):
    mobile = serializers.RegexField(
        regex=Regex.MOBILE,
        error_messages={"invalid": ValidationMessages.INVALID_MOBILE},
    )
    code = serializers.CharField(max_length=6)


class SendLoginSMSCodeInputSerializer(serializers.Serializer):
    mobile = serializers.RegexField(
        regex=Regex.MOBILE,
        error_messages={"invalid": ValidationMessages.INVALID_MOBILE},
    )

    def validate(self, attrs):
        request = self.context["request"]

        mobile = attrs["mobile"]

        system_user = SystemUserService.get_by_mobile(mobile)
        if not system_user:
            raise ApplicationException(_("用户未注册"))

        limiter = VerificationCodeLimiter(mobile, HeaderUtil(request).get_client_ip())

        can_send, message = limiter.can_send_code()
        if not can_send:
            raise ApplicationException(message)

        SMSService.send_login_code(mobile, 6)

        limiter.record_code_sent()

        return attrs


class SendMFASMSCodeInputSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=32)

    def validate(self, attrs):
        request = self.context["request"]

        token = attrs["token"]

        user_id, mfa_type = MFAService.get_user_id_and_mfa_type_by_token(token)
        if not user_id:
            raise ApplicationException(_("请先登录"))

        if mfa_type != SystemUser.MFA_TYPE_SMS:
            raise ApplicationException(_("MFA 未开启短信验证"))

        user = SystemUserService.get_by_id(user_id)
        if not user:
            raise ApplicationException(_("用户不存在"))

        limiter = VerificationCodeLimiter(
            user.mobile, HeaderUtil(request).get_client_ip()
        )

        can_send, message = limiter.can_send_code()
        if not can_send:
            raise ApplicationException(message)

        SMSService.send_mfa_code(user.mobile, 6)

        limiter.record_code_sent()

        return attrs


class MAFVerifyInputSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=32)
    mfa_code = serializers.CharField(max_length=32)

    def validate(self, attrs):
        token = attrs["token"]

        user_id, mfa_type = MFAService.get_user_id_and_mfa_type_by_token(token)
        if not user_id:
            raise ApplicationException(_("请先登录"))

        if mfa_type != SystemUser.MFA_TYPE_TOTP:
            raise ApplicationException(_("MFA未开启 TOTP 验证"))

        attrs["user_id"] = user_id
        return attrs


class TokenRefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    @staticmethod
    def validate_refresh(refresh):
        try:
            refresh_token = RefreshToken(refresh)
        except TokenError:
            raise AuthenticationFailed(_("refresh token decode error")) from TokenError

        value = cache.zscore(AuthConstants.REFRESH_TOKEN_BLACKLIST, refresh)
        if value and value > timezone.now().timestamp():
            raise AuthenticationFailed(_("refresh token in blacklist"))

        return refresh_token
