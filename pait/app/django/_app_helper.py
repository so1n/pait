import importlib
from dataclasses import MISSING
from typing import Any

from django.conf import settings
from django.http import HttpRequest as _Request
from django.views import View

from pait.app.base import BaseAppHelper
from pait.app.django.adapter.attribute import get_app_attribute
from pait.app.django.adapter.request import Request, RequestExtend

__all__ = ["AppHelper", "RequestExtend"]


class AppHelper(BaseAppHelper[_Request, RequestExtend]):
    CbvType = (View,)
    app_name = "django"

    request_class = Request

    def get_attributes(self, key: str, default: Any = MISSING) -> Any:
        value = getattr(self.raw_request, key, MISSING)
        if value is MISSING:
            urlconf = importlib.import_module(settings.ROOT_URLCONF)
            value = get_app_attribute(getattr(urlconf, "urlpatterns", None), key, default)
        if value is MISSING:
            raise KeyError(f"{key} not found")
        return value
