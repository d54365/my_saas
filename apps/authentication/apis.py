import datetime

from accounts.services.system_user import SystemUserService
from common.services.jwt import SystemUserJWTAuthentication
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings

from .constants import AuthConstants
from .serializers import (
    MAFVerifyInputSerializer,
    PasswordLoginInputSerializer,
    SendLoginSMSCodeInputSerializer,
    SendMFASMSCodeInputSerializer,
    SMSLoginInputSerializer,
    TokenRefreshInputSerializer,
)
from .services.base_login import BaseLoginService
from .services.mfa import MFAService
from .services.password_login import PasswordLoginService
from .services.sms_login import SMSLoginService


class SystemUserAuthenticationViewSet(viewsets.ViewSet):
    @action(methods=["POST"], detail=False, url_path="login/password")
    def pwd_login(self, request):
        serializer = PasswordLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PasswordLoginService()
        data = service.authenticate(request=request, **serializer.validated_data)
        return Response(data)

    @action(methods=["POST"], detail=False, url_path="login/sms")
    def sms_login(self, request):
        serializer = SMSLoginInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        service = SMSLoginService()
        data = service.authenticate(request=request, **serializer.validated_data)
        return Response(data)

    @action(methods=["POST"], detail=False, url_path="login/sms-code")
    def send_login_sms_code(self, request):
        serializer = SendLoginSMSCodeInputSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response()

    @action(methods=["POST"], detail=False, url_path="mfa/sms-code")
    def send_mfa_sms_code(self, request):
        serializer = SendMFASMSCodeInputSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response()

    @action(methods=["POST"], detail=False, url_path="mfa/verify")
    def mfa_verify(self, request):
        serializer = MAFVerifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = SystemUserService.get_by_id(serializer.validated_data["user_id"])

        MFAService.verify_mfa(
            user,
            serializer.validated_data["mfa_code"],
            serializer.validated_data["token"],
        )
        data = BaseLoginService.generate_session_data(request, user)
        return Response(data)

    @action(methods=["POST"], detail=False, url_path="token-refresh")
    def token_refresh(self, request):
        serializer = TokenRefreshInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        device_id = refresh_token["device_id"]
        user_id = refresh_token[api_settings.USER_ID_CLAIM]

        access = str(refresh_token.access_token)
        access_expired_second = int(refresh_token.access_token.lifetime.total_seconds())
        access_expired_time = refresh_token.access_token.payload["exp"]

        device_session_key = AuthConstants.SYSTEM_USER_DEVICE_SESSION_TEMPLATE.format(
            user_id=user_id,
            device_id=device_id,
        )
        session_data = cache.get(device_session_key)
        if session_data:
            old_access = session_data["access"]
            old_access_expired_time = session_data["access_expired_time"]
            SystemUserJWTAuthentication().add_access_to_blacklist(
                old_access,
                old_access_expired_time,
            )

            now = timezone.now()
            session_data["access"] = access
            session_data["access_expired_second"] = access_expired_second
            session_data["access_expired_time"] = access_expired_time

            # 动态计算剩余 TTL
            refresh_expired_at = session_data["login_at"] + datetime.timedelta(
                seconds=session_data["refresh_expired_second"],
            )
            remaining_ttl = (refresh_expired_at - now).total_seconds()

            if remaining_ttl > 0:
                cache.set(device_session_key, session_data, timeout=int(remaining_ttl))

        return Response(
            {
                "access": access,
                "access_expire_second": access_expired_second,
            }
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="logout",
        authentication_classes=(SystemUserJWTAuthentication,),
    )
    def logout(self, request):
        user = request.user
        device_id = request.auth.get("device_id")

        SystemUserService.logout_session(user.id, device_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
