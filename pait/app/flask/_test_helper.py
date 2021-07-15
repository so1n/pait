from typing import Dict, Generic, List, Optional, TypeVar

from flask import Response
from flask.testing import FlaskClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

_T = TypeVar("_T", bound=Response)
__all__ = ["FlaskTestHelper"]


class FlaskTestHelper(BaseTestHelper, Generic[_T]):
    client: FlaskClient

    def _app_init_field(self) -> None:
        if self.file_dict:
            if self.form_dict:
                self.form_dict.update(self.file_dict)
            else:
                self.form_dict = self.file_dict

        if self.cookie_dict:
            for key, value in self.cookie_dict.items():
                self.client.set_cookie("localhost", key, value)

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.application)

    def _assert_response(self, resp: Response) -> None:
        if not self.pait_core_model.response_model_list:
            return

        for response_model in self.pait_core_model.response_model_list:
            check_list: List[bool] = [
                resp.status_code in response_model.status_code,
                resp.mimetype == response_model.media_type,
            ]
            if response_model.response_data:
                try:
                    response_model.response_data(**resp.get_json())
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

    def _make_response(self, method: str) -> Response:
        return self.client.open(
            self.path, data=self.form_dict, json=self.body_dict, headers=self.header_dict, method=method
        )
