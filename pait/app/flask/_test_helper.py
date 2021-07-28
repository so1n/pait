from typing import Dict, Optional, Type

from flask import Response
from flask.testing import FlaskClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel

from ._load_app import load_app

__all__ = ["FlaskTestHelper"]


class FlaskTestHelper(BaseTestHelper[Response]):
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

    @staticmethod
    def _check_resp_status(resp: Response, response_model: Type[PaitResponseModel]) -> bool:
        return resp.status_code in response_model.status_code

    @staticmethod
    def _check_resp_media_type(resp: Response, response_model: Type[PaitResponseModel]) -> bool:
        return resp.mimetype == response_model.media_type

    @staticmethod
    def _get_json(resp: Response) -> dict:
        return resp.get_json()

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            return self.path_dict[path_str[1:-1]]
        return None

    def _make_response(self, method: str) -> Response:
        return self.client.open(
            self.path, data=self.form_dict, json=self.body_dict, headers=self.header_dict, method=method
        )
