import binascii
import json
import os
import sys
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Any, Generator, Optional, Tuple
from unittest import mock

import pytest
from tornado.testing import AsyncHTTPTestCase, HTTPResponse
from tornado.web import Application

from example.param_verify.tornado_example import TestCheckParamHandler as CheckParamHandler
from example.param_verify.tornado_example import TestCheckRespHandler as CheckRespHandler
from example.param_verify.tornado_example import TestDependAsyncContextmanagerHanler as DependAsyncContextmanagerHanler
from example.param_verify.tornado_example import TestDependContextmanagerHanler as DependContextmanagerHanler
from example.param_verify.tornado_example import TestGetHandler as GetHandler
from example.param_verify.tornado_example import TestOtherFieldHandler as OtherFieldHandler
from example.param_verify.tornado_example import TestPostHandler as PostHandler
from example.param_verify.tornado_example import (
    TestPreDependAsyncContextmanagerHanler as PreDependAsyncContextmanagerHanler,
)
from example.param_verify.tornado_example import TestPreDependContextmanagerHanler as PreDependContextmanagerHanler
from example.param_verify.tornado_example import create_app
from pait.app import auto_load_app
from pait.app.tornado import TornadoTestHelper
from pait.g import config


@pytest.fixture
def app() -> Generator[Application, None, None]:
    yield create_app()


class TestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return create_app()

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)

    def test_get(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            GetHandler.get,
            path_dict={"age": 3},
            query_dict={"uid": "123", "user_name": "appl", "sex": "man", "multi_user_name": ["abc", "efg"]},
        )
        response: HTTPResponse = self.fetch(
            "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
        )
        for resp in [test_helper.get(), response]:
            resp_dict = json.loads(resp.body.decode())

            assert resp_dict["code"] == 0
            assert resp_dict["data"] == {
                "uid": 123,
                "user_name": "appl",
                "email": "example@xxx.com",
                "age": 3,
                "sex": "man",
                "multi_user_name": ["abc", "efg"],
            }

    def test_check_param(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            CheckParamHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "alias_user_name": "appe"},
        )
        assert (
            "requires at most one of param user_name or alias_user_name"
            in json.loads(test_helper.get().body.decode())["msg"]
        )
        test_helper = TornadoTestHelper(
            self, CheckParamHandler.get, query_dict={"uid": 123, "sex": "man", "age": 10, "alias_user_name": "appe"}
        )
        assert (
            "birthday requires param alias_user_name, which if not none"
            in json.loads(test_helper.get().body.decode())["msg"]
        )

    def test_check_response(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10},
        )
        with pytest.raises(RuntimeError):
            test_helper.get()
        test_helper = TornadoTestHelper(
            self,
            CheckRespHandler.get,
            query_dict={"uid": 123, "user_name": "appl", "sex": "man", "age": 10, "display_age": 1},
        )
        test_helper.get()

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            PreDependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            PreDependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_pre_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            PreDependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            DependContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            DependContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    @mock.patch("example.param_verify.model.logging.error")
    @mock.patch("example.param_verify.model.logging.info")
    def test_depend_async_contextmanager(self, info_logger: Any, error_logger: Any) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123},
        )
        test_helper.get()
        info_logger.assert_called_once_with("context_depend exit")
        test_helper = TornadoTestHelper(
            self,
            DependAsyncContextmanagerHanler.get,
            query_dict={"uid": 123, "is_raise": True},
        )
        test_helper.get()
        error_logger.assert_called_once_with("context_depend error")

    def test_mock_get(self) -> None:
        config.enable_mock_response = True
        resp: dict = json.loads(
            self.fetch(
                "/api/get/3?uid=123&user_name=appl&sex=man&multi_user_name=abc&multi_user_name=efg"
            ).body.decode()
        )
        assert resp == {
            "code": 0,
            "data": {
                "age": 99,
                "email": "example@so1n.me",
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
            },
            "msg": "success",
        }
        config.enable_mock_response = False

    def test_depend(self) -> None:
        response: HTTPResponse = self.fetch(
            "/api/depend?uid=123&user_name=appl",
            method="POST",
            headers={"user-agent": "customer_agent"},
            body='{"age": 2}',
        )
        resp: dict = json.loads(response.body.decode())
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_get_cbv(self) -> None:
        response: HTTPResponse = self.fetch(
            "/api/cbv?uid=123&user_name=appl&age=2", headers={"user-agent": "customer_agent"}
        )
        resp: dict = json.loads(response.body.decode())
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "email": "example@xxx.com", "age": 2}

    def test_post_cbv(self) -> None:
        response: HTTPResponse = self.fetch(
            "/api/cbv",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"uid": 123, "user_name": "appl", "age": 2}',
        )
        resp: dict = json.loads(response.body.decode())
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_post(self) -> None:
        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            PostHandler.post,
            body_dict={"uid": 123, "user_name": "appl", "age": 2, "sex": "man"},
            header_dict={"user-agent": "customer_agent"},
        )
        response: HTTPResponse = self.fetch(
            "/api/post",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"uid": 123, "user_name": "appl", "age": 2, "sex": "man"}',
        )
        for resp in [test_helper.post(), response]:
            resp_dict = json.loads(resp.body.decode())
            assert resp_dict["code"] == 0
            assert resp_dict["data"] == {
                "uid": 123,
                "user_name": "appl",
                "age": 2,
                "content_type": "application/x-www-form-urlencoded",
                "sex": "man",
            }

    def test_pait_model(self) -> None:
        response: HTTPResponse = self.fetch(
            "/api/pait_model?uid=123&user_name=appl",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"age": 2}',
        )
        resp: dict = json.loads(response.body.decode())
        assert resp["code"] == 0
        assert resp["data"] == {"uid": 123, "user_name": "appl", "age": 2, "user_agent": "customer_agent"}

    def test_raise_tip(self) -> None:
        response: HTTPResponse = self.fetch(
            "/api/raise_tip",
            headers={"user-agent": "customer_agent"},
            method="POST",
            body='{"uid": 123, "user_name": "appl", "age": 2}',
        )
        resp: dict = json.loads(response.body.decode())
        assert "msg" in resp

    def test_other_field(self) -> None:
        cookie_str: str = "abcd=abcd;"

        file_content: str = "Hello Word!"

        f1 = NamedTemporaryFile(delete=True)
        file_name: str = f1.name
        f1.write(file_content.encode())
        f1.seek(0)
        f2 = NamedTemporaryFile(delete=True)
        f2.name = file_name  # type: ignore
        f2.write(file_content.encode())
        f2.seek(0)

        test_helper: TornadoTestHelper = TornadoTestHelper(
            self,
            OtherFieldHandler.post,
            cookie_dict={"cookie": cookie_str},
            file_dict={f1.name: f1.read()},
            form_dict={"a": "1", "b": "2", "c": "3"},
        )
        content_type, body = self.encode_multipart_formdata(
            data={"a": "1", "b": "2", "c": "3"}, files={file_name: f2.read()}
        )
        response: HTTPResponse = self.fetch(
            "/api/other_field",
            headers={"cookie": cookie_str, "Content-Type": content_type, "content-length": str(len(body))},
            method="POST",
            body=body,
        )
        for resp in [test_helper.post(), response]:
            assert {
                "filename": file_name,
                "content": file_content,
                "form_a": "1",
                "form_b": "2",
                "form_c": ["3"],
                "cookie": {"abcd": "abcd"},
            } == json.loads(resp.body.decode())["data"]

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

    def test_auto_load_app_class(self) -> None:
        for i in auto_load_app.app_list:
            sys.modules.pop(i, None)
        import starlette

        with mock.patch.dict("sys.modules", sys.modules):
            assert starlette == auto_load_app.auto_load_app_class()
