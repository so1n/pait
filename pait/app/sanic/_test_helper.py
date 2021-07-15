from typing import Dict, Generic, List, Optional, TypeVar

from sanic_testing.testing import SanicTestClient, TestingResponse  # type: ignore

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

_T = TypeVar("_T", bound=TestingResponse)
__all__ = ["SanicTestHelper"]


class SanicTestHelper(BaseTestHelper, Generic[_T]):
    client: SanicTestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)

    def _assert_response(self, resp: TestingResponse) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.status in response_model.status_code,
                resp.content_type == response_model.media_type,
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**resp.json)
                    check_list.append(True)
                except:
                    check_list.append(False)
            if all(check_list):
                return
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}. resp:{resp}")

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            return self.path_dict[path_str[1:-1]]
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
