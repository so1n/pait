import binascii
import json
import os
from io import BytesIO
from typing import Dict, Optional, Tuple, Type

from tornado.testing import AsyncHTTPTestCase, HTTPResponse

from pait.app.base import BaseTestHelper
from pait.model.core import PaitCoreModel
from pait.model.response import PaitResponseModel

from ._load_app import load_app

__all__ = ["TornadoTestHelper"]


class TornadoTestHelper(BaseTestHelper[HTTPResponse]):
    client: AsyncHTTPTestCase

    def _app_init_field(self) -> None:
        if self.cookie_dict:
            self.header_dict.update(self.cookie_dict)
        if "$?" in self.path:
            self.path = self.path.replace("$?", "?")
        elif self.path.endswith("$"):
            self.path = self.path[:-1]

    def _gen_pait_dict(self) -> Dict[str, PaitCoreModel]:
        return load_app(self.client.get_app())

    @staticmethod
    def _check_resp_status(resp: HTTPResponse, response_model: Type[PaitResponseModel]) -> bool:
        return resp.code in response_model.status_code

    @staticmethod
    def _check_resp_media_type(resp: HTTPResponse, response_model: Type[PaitResponseModel]) -> bool:
        return response_model.media_type in resp.headers["Content-Type"]

    @staticmethod
    def _get_json(resp: HTTPResponse) -> dict:
        return json.loads(resp.body.decode())

    def _replace_path(self, path_str: str) -> Optional[str]:
        if self.path_dict:
            head_index, tail_index = -1, -1
            for index, i in enumerate(path_str):
                if i == "<":
                    head_index = index
                if i == ">":
                    tail_index = index
            if head_index != -1 or tail_index != -1:
                return self.path_dict[path_str[head_index + 1 : tail_index]]
        return None

    def _make_response(self, method: str) -> HTTPResponse:
        method = method.upper()
        if self.file_dict or self.form_dict:
            if method != "POST":
                raise RuntimeError("Must use method post")
            content_type, body = self.encode_multipart_formdata(data=self.form_dict, files=self.file_dict)
            headers: dict = self.header_dict.copy()
            headers.update({"Content-Type": content_type, "content-length": str(len(body))})
            return self.client.fetch(self.path, method="POST", headers=headers, body=body)
        body_bytes: Optional[bytes] = None
        if self.body_dict:
            body_bytes = json.dumps(self.body_dict).encode()
        return self.client.fetch(self.path, method=method, headers=self.header_dict, body=body_bytes)

    @staticmethod
    def choose_boundary() -> str:
        """
        Our embarrassingly-simple replacement for mimetools.choose_boundary.
        """
        boundary: bytes = binascii.hexlify(os.urandom(16))
        return boundary.decode("ascii")

    def encode_multipart_formdata(self, data: Optional[dict] = None, files: Optional[dict] = None) -> Tuple[str, bytes]:
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
        uploaded as files.
        Return (content_type, body) ready for httplib.HTTP instance
        """
        body: BytesIO = BytesIO()
        boundary: str = self.choose_boundary()
        if data:
            for key, value in data.items():
                body.write(("--%s\r\n" % boundary).encode(encoding="utf-8"))
                body.write(('Content-Disposition:form-data;name="%s"\r\n' % key).encode(encoding="utf-8"))
                body.write("\r\n".encode(encoding="utf-8"))
                if isinstance(value, int):
                    value = str(value)
                body.write(("%s\r\n" % value).encode(encoding="utf-8"))

        if files:
            for key, value in files.items():
                body.write(("--%s\r\n" % boundary).encode(encoding="utf-8"))
                body.write(
                    ('Content-Disposition:form-data;name="file";filename="%s"\r\n' % key).encode(encoding="utf-8")
                )
                body.write("\r\n".encode(encoding="utf-8"))
                body.write(value)
                body.write("\r\n".encode(encoding="utf-8"))

        body.write(("--%s--\r\n" % boundary).encode(encoding="utf-8"))
        content_type: str = "multipart/form-data;boundary=%s" % boundary
        return content_type, body.getvalue()
