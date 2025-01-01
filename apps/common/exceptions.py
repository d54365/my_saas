import traceback
from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler


class ApplicationException(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}


def log_exception(exc: Exception, context: Dict[str, Any]):
    """记录异常详细信息, 包括上下文和堆栈信息"""
    stack_trace = traceback.format_exc()
    print(
        {
            "exception": str(exc),
            "context": context,
            "stack_trace": stack_trace,
        }
    )


def exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """自定义异常处理, 提供统一的响应结构和日志记录"""
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))
    elif isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied

    response = drf_exception_handler(exc, context)

    exception_log_data = (
        {
            "api": context["request"].path,
            "method": context["request"].method,
            "body": context["request"].data,
            "query_params": context["request"].query_params,
        }
        if context
        else {}
    )

    # 未处理的异常(如服务器错误等)
    if response is None:
        if isinstance(exc, ApplicationException):
            data = {"notification": exc.message, "extra": exc.extra}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # 记录错误日志
        log_exception(exc, exception_log_data)

        data = {"notification": _("服务器开了小差, 请稍后再试"), "extra": {}}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, exceptions.ValidationError):
        response.data = {
            "notification": "Validation error",
            "extra": {"fields": response.data.get("detail", response.data)},
        }
    else:
        response.data = {
            "notification": response.data.get("detail", "Error occurred"),
            "extra": {},
        }

    response.data.pop("detail", None)

    return response


def page_error(exception: Exception) -> JsonResponse:
    """
    全局页面错误处理，将异常通过自定义 exception_handler 处理并返回 JSON 响应。
    中间件里抛出异常, exception_handler里不能捕获到, 通过 handler500 来处理
    """
    response = exception_handler(exception, {})
    return JsonResponse(response.data, status=response.status_code)
