from hashlib import md5

from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from user_agents import parse


class HeaderUtil:
    USER_AGENT_KEY_TEMPLATE = "header:user_agent:{user_agent_md5}"

    def __init__(self, request):
        self.request = request
        self.disk_cache = caches["disk"]

    def get_header(self, header_name, default=None):
        return self.request.META.get(header_name, default)

    def get_client_ip(self):
        x_forwarded_for = self.get_header("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.get_header("REMOTE_ADDR")
        try:
            validate_ipv46_address(ip)
            return ip
        except ValidationError:
            return "127.0.0.1"

    def get_user_agent(self, user_agent: str = None):
        if not user_agent:
            user_agent = self.get_header("HTTP_USER_AGENT", "")

        user_agent_md5 = md5(user_agent.encode(), usedforsecurity=False).hexdigest()

        key = self.USER_AGENT_KEY_TEMPLATE.format(user_agent_md5=user_agent_md5)

        value = self.disk_cache.get(key)
        if value is not None:
            return value

        parsed_ua = parse(user_agent)
        value = {
            "user_agent": user_agent,
            "device_family": parsed_ua.device.family or "",
            "device_brand": parsed_ua.device.brand or "",
            "device_model": parsed_ua.device.model or "",
            "device_type": "Mobile"
            if parsed_ua.is_mobile
            else "Tablet"
            if parsed_ua.is_tablet
            else "PC",
            "os_family": parsed_ua.os.family or "",
            "os_version": parsed_ua.os.version_string or "",
            "browser_family": parsed_ua.browser.family or "",
            "browser_version": parsed_ua.browser.version_string or "",
        }
        self.disk_cache.set(key, value)
        return value
