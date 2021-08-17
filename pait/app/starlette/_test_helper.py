from typing import Dict, Optional, Type

from requests import Response as _Response  # type: ignore
from starlette.testclient import TestClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel

from ._load_app import load_app

__all__ = ["StarletteTestHelper"]


class StarletteTestHelper(BaseTestHelper[_Response]):
    client: TestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)  # type: ignore

    @staticmethod
    def _check_resp_status(resp: _Response, response_model: Type[PaitResponseModel]) -> bool:
        return resp.status_code in response_model.status_code

    @staticmethod
    def _check_resp_media_type(resp: _Response, response_model: Type[PaitResponseModel]) -> bool:
        return resp.headers["content-type"] == response_model.media_type

    @staticmethod
    def _get_json(resp: _Response) -> dict:
        return resp.json()

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "{" and path_str[-1] == "}":
            return self.path_dict[path_str[1:-1]]
        return None

    def _make_response(self, method: str) -> _Response:
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
