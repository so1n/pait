from typing import Dict, Generic, List, Optional, TypeVar

from requests import Response as _Response
from starlette.testclient import TestClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

_T = TypeVar("_T", bound=_Response)
__all__ = ["StarletteTestHelper"]


class StarletteTestHelper(BaseTestHelper, Generic[_T]):
    client: TestClient

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.app)  # type: ignore

    def _assert_response(self, resp: _Response) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.status_code in response_model.status_code,
                resp.headers["content-type"] == response_model.media_type,
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**resp.json())
                    check_list.append(True)
                except:
                    check_list.append(False)
            if all(check_list):
                return
        raise RuntimeError(f"response check error by:{self.pait_core_model.response_model_list}. resp:{resp}")

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
