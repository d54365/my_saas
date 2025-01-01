import uuid

from accounts.models import SystemUser
from accounts.services.system_user import SystemUserService
from authentication.constants import AuthConstants
from authentication.services.mfa import MFAService
from common.exceptions import ApplicationException
from common.header import HeaderUtil
from common.services.ip import IPService
from common.utils import auto_mask
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class BaseLoginService:
    LOGIN_TYPE_SMS = "SMS"

    def authenticate(self, **kwargs):
        raise NotImplementedError("Subclass must implement this method")

    @staticmethod
    def check_user(user, login_manager):
        if not user.is_active:
            login_manager.record_failed_attempts()
            raise ApplicationException(_("用户处于禁用状态"))

    @classmethod
    def post_authenticate(cls, request, user, login_type=None):
        """
        登陆后的通用逻辑
        """
        SystemUserService.update_last_login_at(user)

        if (
            login_type == cls.LOGIN_TYPE_SMS
            and user.mfa_type == SystemUser.MFA_TYPE_SMS
        ):
            # 如果短信登录并且 MFA_TYPE 是短信验证, 那么不需要再次进行短信验证
            return cls.generate_session_data(request, user)

        if user.mfa_type != SystemUser.MFA_TYPE_NONE:
            # 检查是否启用了 MFA
            return cls._handle_mfa(user)

        return cls.generate_session_data(request, user)

    @staticmethod
    def _handle_mfa(user):
        mfa_token = MFAService.generate_token(user.id, user.mfa_type)
        response = {
            "mfa_required": True,
            "token": mfa_token,
            "mfa_type": user.mfa_type,
        }
        if user.mfa_type == SystemUser.MFA_TYPE_SMS:
            response["mobile"] = auto_mask(user.mobile)
        return response

    @classmethod
    def generate_session_data(cls, request, user):
        """
        生成会话数据并缓存
        """
        device_id = uuid.uuid4().hex
        refresh = RefreshToken.for_user(user)
        refresh["device_id"] = device_id
        access = refresh.access_token  # noqa
        access["device_id"] = device_id

        access_expired_second = int(access.lifetime.total_seconds())
        refresh_expired_second = int(refresh.lifetime.total_seconds())
        access_expired_time = access.payload["exp"]
        refresh_expired_time = refresh.payload["exp"]

        header_util = HeaderUtil(request=request)
        user_agent = header_util.get_user_agent()
        ip_address = header_util.get_client_ip()
        geo_info = IPService.get_ip_info(ip_address)

        session_data = {
            "refresh": str(refresh),
            "access": str(access),
            "device_info": {
                "device_id": device_id,
                "user_agent": user_agent["user_agent"],
                "device_family": user_agent["device_family"],
                "device_brand": user_agent["device_brand"],
                "device_model": user_agent["device_model"],
                "device_type": user_agent["device_type"],
                "os_family": user_agent["os_family"],
                "os_version": user_agent["os_version"],
                "browser_family": user_agent["browser_family"],
                "browser_version": user_agent["browser_version"],
            },
            "ip_address": ip_address,
            "login_at": timezone.now(),
            "refresh_expired_second": refresh_expired_second,
            "access_expired_second": access_expired_second,
            "refresh_expired_time": refresh_expired_time,
            "access_expired_time": access_expired_time,
            "country": geo_info["country"],
            "region": geo_info["region"],
            "city": geo_info["city"],
            "last_active_at": timezone.now(),
            "nickname": user.nickname,
        }

        # 缓存会话信息
        cls._cache_session_data(user, device_id, session_data, refresh_expired_second)

        return {
            "access": session_data["access"],
            "access_expired_second": session_data["access_expired_second"],
            "refresh": session_data["refresh"],
            "refresh_expired_second": session_data["refresh_expired_second"],
        }

    @staticmethod
    def _cache_session_data(user, device_id, session_data, timeout):
        """
        缓存会话信息
        """
        device_session_key = AuthConstants.SYSTEM_USER_DEVICE_SESSION_TEMPLATE.format(
            user_id=user.id,
            device_id=device_id,
        )
        user_sessions_key = AuthConstants.SYSTEM_USER_ALL_SESSIONS_TEMPLATE.format(
            user_id=user.id,
        )
        cache.set(device_session_key, session_data, timeout=timeout)
        cache.sadd(user_sessions_key, device_id)
        cache.sadd(AuthConstants.SYSTEM_USER_ACTIVE, user.id)
