from typing import Dict, Mapping, Optional

from flask import Response
from flask.testing import FlaskClient

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel

from ._load_app import load_app

__all__ = ["FlaskTestHelper", "TestHelper"]


class TestHelper(BaseTestHelper[Response]):
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
    def _get_status_code(resp: Response) -> int:
        return resp.status_code

    @staticmethod
    def _get_content_type(resp: Response) -> str:
        return resp.mimetype or ""

    @staticmethod
    def _get_headers(resp: Response) -> Mapping:
        return resp.headers  # type: ignore

    @staticmethod
    def _get_json(resp: Response) -> dict:
        return resp.get_json()

    @staticmethod
    def _get_text(resp: Response) -> str:
        return resp.get_data().decode()

    @staticmethod
    def _get_bytes(resp: Response) -> bytes:
        return resp.get_data()

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict and path_str[0] == "<" and path_str[-1] == ">":
            return self.path_dict[path_str[1:-1]]
        return None

    def _real_request(self, method: str) -> Response:
        return self.client.open(
            self.path, data=self.form_dict, json=self.body_dict, headers=self.header_dict, method=method
        )


class FlaskTestHelper(TestHelper):
    """Will remove on version 1.0"""
