from typing import Dict, Mapping, Optional

from requests import Response as _Response  # type: ignore
from starlette.testclient import TestClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

__all__ = ["StarletteTestHelper", "TestHelper"]


class TestHelper(BaseTestHelper[_Response]):
    client: TestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict["cookie"] = ";".join([f"{key}={value}" for key, value in self.cookie_dict.items()])

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)  # type: ignore

    @staticmethod
    def _get_status_code(resp: _Response) -> int:
        return resp.status_code

    @staticmethod
    def _get_content_type(resp: _Response) -> str:
        return resp.headers["content-type"]

    @staticmethod
    def _get_text(resp: _Response) -> str:
        return resp.text

    @staticmethod
    def _get_bytes(resp: _Response) -> bytes:
        return resp.content

    @staticmethod
    def _get_json(resp: _Response) -> dict:
        return resp.json()

    @staticmethod
    def _get_headers(resp: _Response) -> Mapping:
        return resp.headers

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "{" and path_str[-1] == "}":
            return self.path_dict[path_str[1:-1]]
        return None

    def _real_request(self, method: str) -> _Response:
        method = method.upper()
        resp: _Response = self.client.request(
            method,
            url=self.path,
            cookies=self.cookie_dict,
            data=self.form_dict,
            json=self.body_dict,
            headers=self.header_dict,
            files=self.file_dict,
        )
        return resp


class StarletteTestHelper(TestHelper):
    """Will remove on version 1.0"""
