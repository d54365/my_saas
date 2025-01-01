from authentication.constants import AuthConstants
from authentication.tasks import update_user_last_active


class UpdateLastActiveMiddleware:
    """中间件，用于更新会话的上次活跃时间"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not hasattr(request, "user"):
            return response

        user = request.user
        if user.is_authenticated and "device_id" in request.auth:
            device_id = request.auth.get("device_id")
            device_session_key = (
                AuthConstants.SYSTEM_USER_DEVICE_SESSION_TEMPLATE.format(
                    user_id=user.id,
                    device_id=device_id,
                )
            )
            update_user_last_active.delay(
                device_session_key=device_session_key, log_result=False
            )

        return response
