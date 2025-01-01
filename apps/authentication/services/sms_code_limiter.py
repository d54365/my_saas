from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class VerificationCodeLimiter:
    def __init__(self, mobile, ip_address):
        self.mobile = mobile
        self.ip_address = ip_address
        self.mobile_key = f"code_sent:mobile:{self.mobile}"
        self.ip_key = f"code_sent:ip:{self.ip_address}"
        self.mobile_daily_key = f"code_sent:daily:{self.mobile}"

    def can_send_code(self):
        """
        检查当前手机号码和IP是否符合发送验证码的条件
        """
        if not self.is_phone_interval_ok():
            return False, _("每60秒只能请求一次代码")

        if not self.is_phone_daily_limit_ok():
            return False, _("您已达到每天10个请求的限制")

        if not self.is_ip_limit_ok():
            return False, _("来自IP的请求太多. 请稍后再试")

        return True, ""

    def is_phone_interval_ok(self):
        """检查手机号 60 秒内是否已经发送过"""
        return cache.get(self.mobile_key) is None

    def is_phone_daily_limit_ok(self):
        """检查手机号是否超过24小时内的发送次数限制"""
        daily_attempts = cache.get(self.mobile_daily_key, 0)
        return daily_attempts < 10

    def is_ip_limit_ok(self):
        """检查相同IP是否在1小时内超过了限制"""
        ip_attempts = cache.get(self.ip_key, 0)
        return ip_attempts < 5

    def record_code_sent(self):
        """
        记录一次验证码发送，包括手机号和IP的相关限制
        """
        # 设置手机号60秒内不能再次请求
        cache.set(self.mobile_key, True, timeout=60)

        # 增加手机号24小时内的请求计数
        daily_attempts = cache.get(self.mobile_daily_key, 0)
        if daily_attempts == 0:
            cache.set(self.mobile_daily_key, daily_attempts + 1, timeout=86400)
        else:
            cache.incr(self.mobile_daily_key)

        # 增加IP地址1小时内的请求计数
        ip_attempts = cache.get(self.ip_key, 0)
        if ip_attempts == 0:
            cache.set(self.ip_key, ip_attempts + 1, timeout=3600)
        else:
            cache.incr(self.ip_key)
