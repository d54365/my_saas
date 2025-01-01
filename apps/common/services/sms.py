import random
import string

from django.core.cache import cache


class SMSService:
    LOGIN_CODE_CACHE_TEMPLATE = "sms:login_code:{mobile}"
    LOGIN_CODE_CACHE_TIMEOUT = 60 * 5  # 5分钟
    MFA_CODE_CACHE_TEMPLATE = "sms:mfa_code:{mobile}"
    MFA_CODE_CACHE_TIMEOUT = 60 * 5  # 5分钟

    @staticmethod
    def generate(length: int) -> str:
        """生成验证码"""
        return "".join(random.sample(string.digits, length))

    @classmethod
    def send_login_code(cls, mobile, length):
        """发送验证码"""
        code = cls.generate(length)
        cache.set(
            cls.LOGIN_CODE_CACHE_TEMPLATE.format(mobile=mobile),
            code,
            cls.LOGIN_CODE_CACHE_TIMEOUT,
        )

    @classmethod
    def verify_login_code(cls, mobile, code) -> bool:
        """验证验证码"""
        value = cache.get(cls.LOGIN_CODE_CACHE_TEMPLATE.format(mobile=mobile))
        if not value or value != code:
            return False
        return True

    @classmethod
    def delete_login_code(cls, mobile):
        cache.delete(cls.LOGIN_CODE_CACHE_TEMPLATE.format(mobile=mobile))

    @classmethod
    def send_mfa_code(cls, mobile, length):
        """发送验证码"""
        code = cls.generate(length)
        cache.set(
            cls.MFA_CODE_CACHE_TEMPLATE.format(mobile=mobile),
            code,
            cls.MFA_CODE_CACHE_TIMEOUT,
        )

    @classmethod
    def verify_mfa_code(cls, mobile, code) -> bool:
        """验证mfa验证码"""
        value = cache.get(cls.MFA_CODE_CACHE_TEMPLATE.format(mobile=mobile))
        if not value or value != code:
            return False
        return True

    @classmethod
    def delete_mfa_code(cls, mobile):
        cache.delete(cls.MFA_CODE_CACHE_TEMPLATE.format(mobile=mobile))
