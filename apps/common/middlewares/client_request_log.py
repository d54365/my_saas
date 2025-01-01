from common.header import HeaderUtil
from common.json import JsonUtil
from common.services.ip import IPService
from common.services.jwt import SystemUserJWTAuthentication
from django.utils import timezone
from log.services import RequestLogService
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class ClientRequestLogMiddleware:
    SENSITIVE_FIELDS = {"password", "token", "secret", "refresh"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = timezone.now()

        system_user_id = self._get_system_user_id(request)

        # 过滤 POST 参数
        post_params = self._get_post_params(request)
        self._filter_post_params(post_params)

        response = self.get_response(request)

        header_util = HeaderUtil(request)

        # 获取 IP 地址
        ip_address = header_util.get_client_ip()

        # 获取地理位置信息
        geo_info = IPService.get_ip_info(ip_address)

        user_agent = header_util.get_user_agent()

        log_data = {
            "api_path": request.path,
            "query_params": JsonUtil.dumps(request.GET.dict()),
            "body_params": JsonUtil.dumps(post_params),
            "created_at": start_time,
            "duration": int((timezone.now() - start_time).total_seconds() * 1000),
            "client_ip": ip_address,
            "country": geo_info["country"],
            "region": geo_info["region"],
            "city": geo_info["city"],
            "time_zone": geo_info["time_zone"],
            "status_code": response.status_code,
            "referer": header_util.get_header("HTTP_REFERER", ""),
            "origin": header_util.get_header("HTTP_ORIGIN", ""),
            "accept_language": header_util.get_header("HTTP_ACCEPT_LANGUAGE", ""),
            "host": header_util.get_header("HTTP_HOST", ""),
            "user_agent": user_agent["user_agent"],
            "device_family": user_agent["device_family"],
            "device_brand": user_agent["device_brand"],
            "device_model": user_agent["device_model"],
            "device_type": user_agent["device_type"],
            "os_family": user_agent["os_family"],
            "os_version": user_agent["os_version"],
            "browser_family": user_agent["browser_family"],
            "browser_version": user_agent["browser_version"],
            "user_id": system_user_id,
            "tenant_id": "",
            "request_id": header_util.get_header("HTTP_X_REQUEST_ID", ""),
        }

        RequestLogService.write_to_queue(log_data)

        return response

    @staticmethod
    def _get_post_params(request):
        if request.method != "POST":
            return {}

        content_type = request.META.get("CONTENT_TYPE", "").lower()
        try:
            if "application/json" in content_type:
                return JsonUtil.loads(request.body)
            elif "application/x-www-form-urlencoded" in content_type:
                return request.POST.dict()
        except Exception as e:
            print(e)
            return {}

        return {}

    def _filter_post_params(self, post_params):
        for field in self.SENSITIVE_FIELDS:
            if field in post_params:
                post_params[field] = "******"

    @staticmethod
    def _get_system_user_id(request):
        system_user_id = None
        try:
            auth = SystemUserJWTAuthentication()
            user, validated_token = auth.authenticate(request)
            system_user_id = user.id
        except (InvalidToken, AuthenticationFailed):
            pass  # Token 无效，视为未登录用户
        return system_user_id
