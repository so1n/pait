from typing import Dict, Mapping, Optional

from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

__all__ = ["SanicTestHelper", "TestHelper"]


class TestHelper(BaseTestHelper[TestingResponse]):
    client: SanicTestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict["cookie"] = ";".join([f"{key}={value}" for key, value in self.cookie_dict.items()])

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)

    @staticmethod
    def _get_status_code(resp: TestingResponse) -> int:
        return resp.status

    @staticmethod
    def _get_content_type(resp: TestingResponse) -> str:
        return resp.content_type

    @staticmethod
    def _get_text(resp: TestingResponse) -> str:
        return resp.text

    @staticmethod
    def _get_bytes(resp: TestingResponse) -> bytes:
        return resp.content

    @staticmethod
    def _get_headers(resp: TestingResponse) -> Mapping:
        return resp.headers

    @staticmethod
    def _get_json(resp: TestingResponse) -> dict:
        return resp.json

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            key: str = path_str[1:-1]
            if ":" in key:
                key = key.split(":")[0]
            return self.path_dict[key]
        return None

    def _real_request(self, method: str) -> TestingResponse:
        method = method.lower()
        if method == "get":
            request, resp = self.client._sanic_endpoint_test(method, uri=self.path, headers=self.header_dict)
        else:
            request, resp = self.client._sanic_endpoint_test(
                method,
                uri=self.path,
                data=self.form_dict,
                json=self.body_dict,
                headers=self.header_dict,
                files=self.file_dict,
            )
        return resp


class SanicTestHelper(TestHelper):
    """Will remove on version 1.0"""
