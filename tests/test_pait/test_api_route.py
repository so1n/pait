from typing import Type

import pytest

from pait.app.base.api_route import BaseAPIRoute
from pait.core import Pait
from pait.field import Body, Query
from pait.model.response import HtmlResponseModel, JsonResponseModel
from pait.model.status import PaitStatus
from pait.model.tag import Tag
from tests.util import FakeAppHelper


class CustomerPait(Pait):
    app_helper_class = FakeAppHelper


class APIRoute(BaseAPIRoute):
    @property
    def _pait_type(self) -> Type[Pait]:
        return CustomerPait


class TestApiRoute:
    def test_init_param_error(self) -> None:

        with pytest.raises(ValueError) as e:
            BaseAPIRoute(CustomerPait(), group="test")

        exec_msg: str = e.value.args[0]
        assert exec_msg == "pait and kwargs can't be used at the same time"

    def test_init_error_pait(self) -> None:
        class CustomerPait1(Pait):
            app_helper_class = FakeAppHelper

        with pytest.raises(TypeError) as e:
            APIRoute(pait=CustomerPait1())
        exec_msg: str = e.value.args[0]
        assert "pait must be" in exec_msg

    def test_include_sub_route(self) -> None:
        with pytest.raises(ValueError):
            APIRoute(CustomerPait(), path="/api").include_sub_route(APIRoute(CustomerPait(), path="/user"))

    def test_merge_same_key_append_param(self) -> None:

        def demo() -> None:
            pass

        def demo_depend1() -> None:
            pass

        def demo_depend2() -> None:
            pass

        user_tag = Tag(name="user-tag", desc="tag desc")
        api_tag = Tag(name="api-tag", desc="tag desc")

        api_route = APIRoute(
            path="/api",
            default_field_class=Body,
            pre_depend_list=[demo_depend1],
            author=("one",),
            desc="api desc",
            summary="api summary",
            status=PaitStatus.test,
            group="api group",
            tag=(api_tag,),
            response_model_list=[HtmlResponseModel],
            sync_to_thread=True,
            feature_code="api",
            extra={"a": 1, "b": 2},
        )
        api_route.add_api_route(
            demo,
            method=["GET"],
            path="/user",
            default_field_class=Query,
            pre_depend_list=[demo_depend2],
            author=("two",),
            desc="user desc",
            summary="user summary",
            status=PaitStatus.release,
            group="user group",
            tag=(user_tag,),
            response_model_list=[JsonResponseModel],
            sync_to_thread=False,
            feature_code="user",
            extra={"a": 1, "b": 3, "c": 5},
        )
        route_dc = api_route.route[-1]
        assert route_dc.pait_param.get("default_field_class") == Query
        assert route_dc.pait_param.get("pre_depend_list") == [demo_depend2]
        assert route_dc.pait_param.get("author") == ("two",)
        assert route_dc.pait_param.get("desc") == "user desc"
        assert route_dc.pait_param.get("summary") == "user summary"
        assert route_dc.pait_param.get("status") == PaitStatus.release
        assert route_dc.pait_param.get("group") == "user group"
        assert route_dc.pait_param.get("tag") == (user_tag,)
        assert route_dc.pait_param.get("response_model_list") == [JsonResponseModel]
        # assert route_dc.pait_param.get("sync_to_thread") is False
        assert route_dc.pait_param.get("feature_code") == "user"
        assert route_dc.pait_param.get("extra") == {"a": 1, "b": 3, "c": 5}

        api_route.add_api_route(
            demo,
            method=["GET"],
            path="/user2",
            append_pre_depend_list=[demo_depend2],
            append_author=("two",),
            append_tag=(Tag(name="user-tag", desc="tag desc"),),
            append_response_model_list=[JsonResponseModel],
            extra={"a": 1, "b": 3, "c": 5},
        )
        route_dc = api_route.route[-1]
        assert route_dc.pait_param.get("pre_depend_list") == [demo_depend1, demo_depend2]
        assert route_dc.pait_param.get("author") == ("one", "two")
        assert route_dc.pait_param.get("tag") == (api_tag, user_tag)
        assert route_dc.pait_param.get("response_model_list") == [HtmlResponseModel, JsonResponseModel]
        assert route_dc.pait_param.get("extra") == {"a": 1, "b": 3, "c": 5}

    def test_http_method(self) -> None:
        def demo() -> None:
            pass

        api_route = APIRoute(CustomerPait(), framework_extra_param={"a": 1, "b": 2})

        for http_method in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]:
            getattr(api_route, http_method.lower())(path="/api", framework_extra_param={"b": 3, "c": 5})(demo)
            assert api_route.route[-1].method_list == [http_method]
            assert api_route.route[-1].path == "/api"
            assert api_route.route[-1].framework_extra_param == {"a": 1, "b": 3, "c": 5}
