from threading import local

_thread_locals = local()


def get_current_tenant():
    return getattr(_thread_locals, "tenant_id", None)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.headers.get("X-Tenant-ID")

        if tenant_id is not None and self.validate_tenant_id(tenant_id):
            _thread_locals.tenant_id = int(tenant_id)
        else:
            _thread_locals.tenant_id = None

        response = self.get_response(request)

        _thread_locals.tenant_id = None

        return response

    @staticmethod
    def validate_tenant_id(tenant_id):
        try:
            tenant_id = int(tenant_id)
            return tenant_id > 0
        except (TypeError, ValueError):
            return False
