import uuid

import pyotp
from accounts.models import SystemUser
from common.exceptions import ApplicationException
from common.services.sms import SMSService
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class MFAService:
    MFA_TOKEN_TEMPLATE = "authentication:mfa:{token}"  # nosec
    MFA_TOKEN_TIMEOUT = 60 * 15

    @classmethod
    def generate_token(cls, user_id, mfa_type):
        token = uuid.uuid4().hex
        cache.set(
            cls.MFA_TOKEN_TEMPLATE.format(token=token),
            f"{user_id}_{mfa_type}",
            cls.MFA_TOKEN_TIMEOUT,
        )
        return token

    @classmethod
    def get_user_id_and_mfa_type_by_token(cls, token):
        value = cache.get(cls.MFA_TOKEN_TEMPLATE.format(token=token))
        if not value:
            return None, None
        value_list = [int(value) for value in value.split("_")]
        user_id, mfa_type = value_list
        return user_id, mfa_type

    @classmethod
    def _delete_token(cls, token):
        cache.delete(cls.MFA_TOKEN_TEMPLATE.format(token=token))

    @classmethod
    def verify_mfa(cls, user, mfa_code, token):
        if not user:
            raise ApplicationException(_("验证失败"))

        match user.mfa_type:
            case SystemUser.MFA_TYPE_NONE:
                raise ApplicationException(_("用户未开启 MFA"))
            case SystemUser.MFA_TYPE_TOTP:
                if not cls._verify_totp(user.totp_key, mfa_code):
                    raise ApplicationException(_("验证失败"))
            case SystemUser.MFA_TYPE_SMS:
                if not cls._verify_sms_code(user.mobile, mfa_code):
                    raise ApplicationException(_("验证失败"))

        cls._delete_token(token)

    @staticmethod
    def _verify_totp(totp_key, code):
        totp = pyotp.TOTP(totp_key)
        return totp.verify(code)

    @staticmethod
    def _verify_sms_code(mobile, sms_code):
        if not SMSService.verify_mfa_code(mobile, sms_code):
            return False
        SMSService.delete_mfa_code(mobile)
        return True
