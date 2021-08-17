from typing import Dict, Optional, Type

from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel

from ._load_app import load_app

__all__ = ["SanicTestHelper"]


class SanicTestHelper(BaseTestHelper[TestingResponse]):
    client: SanicTestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)

    @staticmethod
    def _check_resp_status(resp: TestingResponse, response_model: Type[PaitResponseModel]) -> bool:
        return resp.status in response_model.status_code

    @staticmethod
    def _check_resp_media_type(resp: TestingResponse, response_model: Type[PaitResponseModel]) -> bool:
        return resp.content_type == response_model.media_type

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

    def _make_response(self, method: str) -> TestingResponse:
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
