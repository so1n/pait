import importlib
import json
from typing import TYPE_CHECKING, Dict, Mapping, Optional

from django.conf import settings

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

if TYPE_CHECKING:
    from django.http import HttpResponse
    from django.test import Client

__all__ = ["DjangoTestHelper", "TestHelper"]


class TestHelper(BaseTestHelper["HttpResponse"]):
    client: "Client"

    def _app_init_field(self) -> None:
        if self.file_dict:
            if self.form_dict:
                self.form_dict.update(self.file_dict)
            else:
                self.form_dict = self.file_dict

        if self.cookie_dict:
            for key, value in self.cookie_dict.items():
                self.client.cookies[key] = value

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        urlconf = importlib.import_module(settings.ROOT_URLCONF)
        return (self._load_app or load_app)(urlconf.urlpatterns)

    @staticmethod
    def _get_status_code(resp: "HttpResponse") -> int:
        return resp.status_code

    @staticmethod
    def _get_content_type(resp: "HttpResponse") -> str:
        return resp.headers["Content-Type"]

    @staticmethod
    def _get_text(resp: "HttpResponse") -> str:
        return resp.content.decode()

    @staticmethod
    def _get_bytes(resp: "HttpResponse") -> bytes:
        try:
            return resp.content
        except AttributeError:
            return b"".join(resp.streaming_content)

    @staticmethod
    def _get_json(resp: "HttpResponse") -> dict:
        return json.loads(resp.content.decode())

    @staticmethod
    def _get_headers(resp: "HttpResponse") -> Mapping:
        return resp.headers

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "{" and path_str[-1] == "}":
            return self.path_dict[path_str[1:-1]]
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            key = path_str[1:-1]
            if ":" in key:
                key = key.split(":", 1)[1]
            return self.path_dict[key]
        return None

    def _real_request(self, method: str) -> "HttpResponse":
        extra = {"HTTP_" + key.upper().replace("-", "_"): value for key, value in self.header_dict.items()}
        method_handler = getattr(self.client, method.lower())
        if self.file_dict or self.form_dict:
            data = {}
            if self.form_dict:
                data.update(self.form_dict)
            if self.file_dict:
                data.update(self.file_dict)
            return method_handler(self.path, data=data, **extra)
        if self.body_dict:
            return method_handler(self.path, data=json.dumps(self.body_dict), content_type="application/json", **extra)
        return method_handler(self.path, **extra)


class DjangoTestHelper(TestHelper):
    pass
