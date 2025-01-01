from accounts.services.system_user import SystemUserService
from authentication.constants import AuthConstants
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings


class SystemUserJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raise InvalidToken(_("header is valid"))

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            raise InvalidToken(_("token is valid"))

        validated_token = self.get_validated_token(raw_token)

        value = cache.zscore(
            AuthConstants.ACCESS_TOKEN_BLACKLIST,
            validated_token.token.decode(),  # noqa
        )
        if value and value > timezone.now().timestamp():
            raise AuthenticationFailed(_("token in blacklist"))

        user = self.get_user(validated_token)
        device_id = validated_token.get("device_id")

        return user, {"token": validated_token, "device_id": device_id}

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))  # noqa

        user = SystemUserService.get_by_id(user_id)
        if not user:
            raise AuthenticationFailed(_("user not exists"))
        if not user.is_active:
            raise PermissionDenied(_("账号被禁用中"))
        return user

    @staticmethod
    def add_access_to_blacklist(access_token, access_token_exp):
        cache.zadd(
            AuthConstants.ACCESS_TOKEN_BLACKLIST,
            {
                str(access_token): access_token_exp,
            },
        )

    @staticmethod
    def add_refresh_to_blacklist(refresh, refresh_exp):
        cache.zadd(
            AuthConstants.REFRESH_TOKEN_BLACKLIST,
            {
                str(refresh): refresh_exp,
            },
        )
