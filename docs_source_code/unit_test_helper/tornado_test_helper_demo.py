# flake8: noqa: E402
from typing import Type

from pydantic import BaseModel, Field
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.field import Body
from pait.model.response import JsonResponseModel


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


class DemoHandler(RequestHandler):
    @pait(response_model_list=[DemoResponseModel])
    def post(
        self,
        uid: int = Body.t(description="user id", gt=10, lt=1000),
        username: str = Body.t(description="user name", min_length=2, max_length=4),
        return_error_resp: bool = Body.i(description="return error resp", default=False),
    ) -> None:
        if return_error_resp:
            self.write({})
        else:
            self.write({"uid": uid, "user_name": username})


app: Application = Application([(r"/api", DemoHandler)])

from tornado.testing import AsyncHTTPTestCase

#############
# unit test #
#############
from pait.app.tornado import TornadoTestHelper


class TestTornado(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return app

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://localhost:%s%s" % (self.get_protocol(), self.get_http_port(), path)

    def test_demo_post_route_by_call_json(self) -> None:
        test_helper = TornadoTestHelper(
            client=self,
            func=DemoHandler.post,
            body_dict={"uid": 11, "username": "test"},
        )
        assert test_helper.json() == {"uid": 11, "user_name": "test"}

    def test_demo_post_route_by_use_method(self) -> None:
        test_helper = TornadoTestHelper(
            client=self,
            func=DemoHandler.post,
            body_dict={"uid": 11, "username": "test"},
        )
        assert test_helper.json(method="POST") == {"uid": 11, "user_name": "test"}

    def test_demo_post_route_by_raw_web_framework_response(self) -> None:
        test_helper = TornadoTestHelper(
            client=self,
            func=DemoHandler.post,
            body_dict={"uid": 11, "username": "test"},
        )
        resp = test_helper.post()
        assert resp.code == 200
        assert resp.body.decode() == '{"uid": 11, "user_name": "test"}'

    def test_demo_post_route_by_test_helper_check_response_error(self) -> None:
        test_helper = TornadoTestHelper(
            client=self,
            func=DemoHandler.post,
            body_dict={"uid": 11, "username": "test", "return_error_resp": True},
        )
        assert test_helper.json() == {"uid": 11, "user_name": "test"}
