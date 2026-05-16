import sys
import types
from typing import Any, Callable, List, Sequence

import django
from django.apps import apps
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import path
from django.views.decorators.http import require_http_methods
from pydantic import ValidationError

from pait.app.django import Pait, load_app
from pait.app.django.adapter.exception import DjangoHTTPException
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.model.status import PaitStatus

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)
API_EXCEPTION_MIDDLEWARE: str = "example.django_example.utils.ApiExceptionMiddleware"


def api_exception(request: HttpRequest, exc: Exception) -> HttpResponse:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return JsonResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, PaitBaseException):
        return JsonResponse({"code": -1, "msg": str(exc)})
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JsonResponse({"code": -1, "msg": f"miss param: {error_param_list}"})
    elif isinstance(exc, DjangoHTTPException):
        resp = HttpResponse(str(exc), status=exc.status_code)
        for key, value in exc.headers.items():
            resp.headers[key] = value
        return resp
    return JsonResponse({"code": -1, "msg": str(exc)})


class ApiExceptionMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exc: Exception) -> HttpResponse:
        return api_exception(request, exc)


def get_middleware() -> List[str]:
    middleware_list: List[str] = list(getattr(settings, "MIDDLEWARE", []))
    if API_EXCEPTION_MIDDLEWARE not in middleware_list:
        middleware_list.append(API_EXCEPTION_MIDDLEWARE)
    return middleware_list


def method_route(route: Any, methods: Sequence[str]) -> Any:
    method_set = {method.upper() for method in methods}
    route = require_http_methods(list(method_set))(route)
    setattr(route, "_pait_method_set", method_set)
    return route


def route_path(url: str, route: Any, methods: Sequence[str], **kwargs: Any) -> Any:
    return path(url, method_route(route, methods), **kwargs)


def configure_urlpatterns(urlpatterns: List[Any], module_name: str) -> None:
    urlconf_module = types.ModuleType(module_name)
    setattr(urlconf_module, "urlpatterns", urlpatterns)
    sys.modules[module_name] = urlconf_module
    if not settings.configured:
        settings.configure(
            ALLOWED_HOSTS=["127.0.0.1", "localhost", "testserver"],
            DEFAULT_CHARSET="utf-8",
            DEBUG=True,
            MIDDLEWARE=[API_EXCEPTION_MIDDLEWARE],
            ROOT_URLCONF=module_name,
            SECRET_KEY="pait-django-example",
        )
    else:
        settings.MIDDLEWARE = get_middleware()
        settings.ROOT_URLCONF = module_name
    if not apps.ready:
        django.setup()


def run_urlpatterns(urlpatterns: List[Any], module_name: str, port: int = 8000) -> None:
    configure_urlpatterns(urlpatterns, module_name)
    load_app(urlpatterns, overwrite_already_exists_data=True)
    execute_from_command_line(["manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"])
