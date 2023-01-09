from __future__ import annotations

import hashlib
import time
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional, Tuple

import grpc
from flask import Flask, Request, Response, make_response, send_from_directory
from flask.views import MethodView
from pydantic import BaseModel, ValidationError
from redis import Redis  # type: ignore
from typing_extensions import TypedDict
from werkzeug.exceptions import HTTPException

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc
from example.param_verify.common import tag
from example.param_verify.common.depend import GetUserDepend, context_depend, demo_depend
from example.param_verify.common.request_model import SexEnum, TestPaitModel, UserModel, UserOtherModel
from example.param_verify.common.response_model import (
    AutoCompleteRespModel,
    FailRespModel,
    FileRespModel,
    HtmlRespModel,
    LoginRespModel,
    NotAuthenticatedRespModel,
    SimpleRespModel,
    SuccessRespModel,
    TextRespModel,
    UserSuccessRespModel,
    UserSuccessRespModel2,
    UserSuccessRespModel3,
    gen_response_model_handle,
)
from pait.app import set_app_attribute
from pait.app.flask import AddDocRoute, Pait, add_doc_route, load_app, pait
from pait.app.flask.grpc_route import GrpcGatewayRoute
from pait.app.flask.plugin.auto_complete_json_resp import AutoCompleteJsonRespPlugin
from pait.app.flask.plugin.cache_resonse import CacheResponsePlugin
from pait.app.flask.plugin.check_json_resp import CheckJsonRespPlugin
from pait.app.flask.plugin.mock_response import MockPlugin
from pait.app.flask.security.api_key import api_key
from pait.exceptions import PaitBaseException, PaitBaseParamException, TipException
from pait.extra.config import MatchRule, apply_block_http_method_set, apply_extra_openapi_model
from pait.field import Cookie, Depends, File, Form, Header, Json, MultiForm, MultiQuery, Path, Query
from pait.g import config
from pait.model.links import LinksModel
from pait.model.response import HtmlResponseModel
from pait.model.status import PaitStatus
from pait.model.template import TemplateVar
from pait.plugin.at_most_one_of import AtMostOneOfPlugin
from pait.plugin.required import RequiredPlugin

global_pait: Pait = Pait(author=("so1n",), status=PaitStatus.test)

user_pait: Pait = global_pait.create_sub_pait(group="user")
check_resp_pait: Pait = global_pait.create_sub_pait(group="check_resp", tag=(tag.check_resp_tag,))
link_pait: Pait = global_pait.create_sub_pait(
    group="links",
    status=PaitStatus.release,
    tag=(tag.links_tag,),
)
plugin_pait: Pait = global_pait.create_sub_pait(
    group="plugin",
    status=PaitStatus.release,
    tag=(tag.plugin_tag,),
)
other_pait: Pait = pait.create_sub_pait(author=("so1n",), status=PaitStatus.test, group="other")


def api_exception(exc: Exception) -> Dict[str, Any]:
    if isinstance(exc, TipException):
        exc = exc.exc

    if isinstance(exc, PaitBaseParamException):
        return {"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"}
    elif isinstance(exc, PaitBaseException):
        return {"code": -1, "msg": str(exc)}
    elif isinstance(exc, ValidationError):
        error_param_list: list = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return {"code": -1, "msg": f"miss param: {error_param_list}"}
    elif isinstance(exc, HTTPException):
        raise exc
    return {"code": -1, "msg": str(exc)}


@other_pait(
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=(tag.raise_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def raise_tip_route(
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> dict:
    """Prompted error from pait when test does not find value"""
    return {"code": 0, "msg": "", "data": {"content_type": content__type}}


@user_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.post_tag),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
def post_route(
    model: UserModel = Json.i(raw_return=True),
    other_model: UserOtherModel = Json.i(raw_return=True),
    sex: SexEnum = Json.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> dict:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return {"code": 0, "msg": "", "data": return_dict}


@other_pait(
    status=PaitStatus.release,
    tag=(tag.user_tag, tag.depend_tag),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
    user_model: UserModel = Depends.i(GetUserDepend()),
) -> dict:
    """Testing depend and using request parameters"""
    assert request is not None, "Not found request"
    return {
        "code": 0,
        "msg": "",
        "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
    }


@other_pait(
    status=PaitStatus.release,
    tag=(tag.same_alias_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def same_alias_route(
    query_token: str = Query.i("", alias="token"), header_token: str = Header.i("", alias="token")
) -> dict:
    """Test different request types, but they have the same alias and different parameter names"""
    return {"code": 0, "msg": "", "data": {"query_token": query_token, "header_token": header_token}}


@user_pait(
    status=PaitStatus.test,
    tag=(tag.field_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def field_default_factory_route(
    demo_value: int = Json.i(description="Json body value not empty"),
    data_list: List[str] = Json.i(default_factory=list, description="test default factory"),
    data_dict: Dict[str, Any] = Json.i(default_factory=dict, description="test default factory"),
) -> dict:
    return {"code": 0, "msg": "", "data": {"demo_value": demo_value, "data_list": data_list, "data_dict": data_dict}}


@user_pait(
    status=PaitStatus.release,
    tag=(tag.field_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)
def pait_base_field_route(
    upload_file: Any = File.i(description="upload file"),
    a: str = Form.i(description="form data"),
    b: str = Form.i(description="form data"),
    c: List[str] = MultiForm.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test the use of all BaseField-based"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            "filename": upload_file.filename,
            "content": upload_file.read().decode(),
            "form_a": a,
            "form_b": b,
            "form_c": c,
            "cookie": cookie,
            "multi_user_name": multi_user_name,
            "age": age,
            "uid": uid,
            "user_name": user_name,
            "email": email,
            "sex": sex,
        },
    }


@user_pait(
    status=PaitStatus.release,
    tag=(tag.check_param_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
    post_plugin_list=[
        RequiredPlugin.build(required_dict={"birthday": ["alias_user_name"]}),
        AtMostOneOfPlugin.build(at_most_one_of_list=[["user_name", "alias_user_name"]]),
    ],
)
def check_param_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    alias_user_name: Optional[str] = Query.i(None, description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    birthday: Optional[str] = Query.i(None, description="birthday"),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test check param"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            "birthday": birthday,
            "uid": uid,
            "user_name": user_name or alias_user_name,
            "email": email,
            "age": age,
            "sex": sex.value,
        },
    }


@user_pait(
    status=PaitStatus.release,
    tag=(tag.check_resp_tag,),
    response_model_list=[UserSuccessRespModel3, FailRespModel],
)
def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> dict:
    """Test test-helper check response"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict


@user_pait(
    status=PaitStatus.release,
    tag=(tag.mock_tag,),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    plugin_list=[MockPlugin.build()],
)
def mock_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test gen mock response"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
            "age": age,
            "sex": sex.value,
            "multi_user_name": multi_user_name,
        },
    }


@other_pait(status=PaitStatus.test, tag=(tag.field_tag,), response_model_list=[SimpleRespModel, FailRespModel])
def pait_model_route(test_pait_model: TestPaitModel) -> dict:
    """Test pait model"""
    return {"code": 0, "msg": "", "data": test_pait_model.dict()}


@other_pait(status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, FailRespModel])
def depend_contextmanager_route(uid: str = Depends.i(context_depend), is_raise: bool = Query.i(default=False)) -> dict:
    if is_raise:
        raise RuntimeError("test")
    return {"code": 0, "msg": uid}


@other_pait(
    status=PaitStatus.test,
    tag=(tag.depend_tag,),
    pre_depend_list=[context_depend],
    response_model_list=[SuccessRespModel, FailRespModel],
)
def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> dict:
    if is_raise:
        raise RuntimeError()
    return {"code": 0, "msg": ""}


class CbvRoute(MethodView):
    content_type: str = Header.i(alias="Content-Type")

    @user_pait(
        status=PaitStatus.release,
        tag=(tag.cbv_tag,),
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Query.i(description="sex"),
        model: UserOtherModel = Query.i(raw_return=True),
    ) -> dict:
        """Text cbv route get"""
        return {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "sex": sex.value,
                "age": model.age,
                "content_type": self.content_type,
            },
        }

    @user_pait(
        desc="test cbv post method",
        tag=(tag.cbv_tag,),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    def post(
        self,
        uid: int = Json.i(description="user id", gt=10, lt=1000),
        user_name: str = Json.i(description="user name", min_length=2, max_length=4),
        sex: SexEnum = Json.i(description="sex"),
        model: UserOtherModel = Json.i(raw_return=True),
    ) -> dict:
        """Text cbv route post"""
        return {
            "code": 0,
            "msg": "",
            "data": {
                "uid": uid,
                "user_name": user_name,
                "sex": sex.value,
                "age": model.age,
                "content_type": self.content_type,
            },
        }


class NotPaitCbvRoute(MethodView):
    user_name: str = Query.i()

    def get(self) -> Response:
        return make_response(self.user_name, 200)

    def post(self) -> Response:
        return make_response(self.user_name, 200)


@check_resp_pait(response_model_list=[TextRespModel])
def text_response_route() -> Response:
    """test return test response"""
    response: Response = make_response(str(time.time()), 200)
    response.mimetype = "text/plain"
    response.headers.add_header("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[HtmlRespModel])
def html_response_route() -> Response:
    """test return html response"""
    response: Response = make_response("<H1>" + str(time.time()) + "</H1>", 200)
    response.mimetype = "text/html"
    response.headers.add_header("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[FileRespModel])
def file_response_route() -> Response:
    """test return file response"""
    file_content: str = "Hello Word!"
    with NamedTemporaryFile(delete=True) as f:
        f.write(file_content.encode())
        f.seek(0)
        _, f_path, f_filename = f.name.split("/")
        response: Response = send_from_directory("/" + f_path, f_filename)
        response.headers.add_header("X-Example-Type", "file")
        return response


@link_pait(response_model_list=[LoginRespModel])
def login_route(uid: str = Json.i(description="user id"), password: str = Json.i(description="password")) -> dict:
    # only use test
    return {"code": 0, "msg": "", "data": {"token": hashlib.sha256((uid + password).encode("utf-8")).hexdigest()}}


@link_pait(response_model_list=[SuccessRespModel])
def get_user_route(
    token: str = Header.i(
        "",
        description="token",
        link=LinksModel(LoginRespModel, "$response.body#/data/token", desc="test links model"),
        example=TemplateVar("token"),
    )
) -> dict:
    if token:
        return {"code": 0, "msg": ""}
    else:
        return {"code": 1, "msg": ""}


@plugin_pait(response_model_list=[AutoCompleteRespModel], plugin_list=[AutoCompleteJsonRespPlugin.build()])
def auto_complete_json_route() -> dict:
    """Test json plugin by resp type is dict"""
    return {
        "code": 0,
        "msg": "",
        "data": {
            # "uid": 0,
            "image_list": [
                {"aaa": 10},
                {"aaa": "123"},
            ],
            "music_list": [
                {
                    "name": "music1",
                    "url": "http://music1.com",
                    "singer": "singer1",
                },
                {
                    # "name": "music1",
                    "url": "http://music1.com",
                    # "singer": "singer1",
                },
            ],
        },
    }


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
def check_json_plugin_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> dict:
    """Test json plugin by resp type is dict"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict


_sub_typed_dict = TypedDict(
    "_sub_typed_dict",
    {
        "uid": int,
        "user_name": str,
        "email": str,
    },
)
_typed_dict = TypedDict(
    "_typed_dict",
    {
        "code": int,
        "msg": str,
        "data": _sub_typed_dict,
    },
)


@plugin_pait(
    response_model_list=[HtmlResponseModel, FailRespModel],
    post_plugin_list=[
        CacheResponsePlugin.build(
            redis=Redis(decode_responses=True),
            cache_time=10,
            include_exc=(RuntimeError,),
            enable_cache_name_merge_param=True,
        )
    ],
)
def cache_response(raise_exc: Optional[int] = Query.i(default=None)) -> Response:
    timestamp_str = str(time.time())
    if raise_exc:
        if raise_exc == 1:
            raise Exception(timestamp_str)
        elif raise_exc == 2:
            raise RuntimeError(timestamp_str)
    else:
        return make_response(timestamp_str, 200)


@plugin_pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
)
def cache_response1() -> Response:
    return make_response(str(time.time()), 200)


def not_pait_route(
    user_name: str = Query.i(),
) -> Response:
    return make_response(user_name, 200)


@plugin_pait(response_model_list=[UserSuccessRespModel3], plugin_list=[CheckJsonRespPlugin.build()])
def check_json_plugin_route1(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> _typed_dict:
    """Test json plugin by resp type is typed dict"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict  # type: ignore


@other_pait(
    status=PaitStatus.test, tag=(tag.depend_tag,), response_model_list=[SuccessRespModel, NotAuthenticatedRespModel]
)
def api_key_route(
    token: str = Depends.i(api_key(name="token", field=Header, verify_api_key_callable=lambda x: x == "my-token"))
) -> dict:
    return {"token": token}


def add_grpc_gateway_route(app: Flask) -> None:
    """Split out to improve the speed of test cases"""
    from typing import Callable, Type
    from uuid import uuid4

    from flask import jsonify

    from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2
    from pait.util.grpc_inspect.stub import GrpcModel
    from pait.util.grpc_inspect.types import Message

    def _make_response(resp_dict: dict) -> Response:
        return jsonify({"code": 0, "msg": "", "data": resp_dict})

    class CustomerGrpcGatewayRoute(GrpcGatewayRoute):
        def gen_route(self, grpc_model: GrpcModel, request_pydantic_model_class: Type[BaseModel]) -> Callable:

            if grpc_model.method in ("/user.User/login_user", "/user.User/create_user"):
                return super().gen_route(grpc_model, request_pydantic_model_class)
            else:

                def _route(
                    request_pydantic_model: request_pydantic_model_class,  # type: ignore
                    token: str = Header.i(description="User Token"),
                    req_id: str = Header.i(alias="X-Request-Id", default_factory=lambda: str(uuid4())),
                ) -> Any:
                    func: Callable = self.get_grpc_func(grpc_model.method)
                    request_dict: dict = request_pydantic_model.dict()  # type: ignore
                    if grpc_model.method == "/user.User/logout_user":
                        # logout user need token param
                        request_dict["token"] = token
                    else:
                        # check token
                        result: user_pb2.GetUidByTokenResult = user_pb2_grpc.UserStub(self.channel).get_uid_by_token(
                            user_pb2.GetUidByTokenRequest(token=token)
                        )
                        if not result.uid:
                            raise RuntimeError(f"Not found user by token:{token}")
                    request_msg: Message = self.get_msg_from_dict(grpc_model.request, request_dict)
                    # add req_id to request
                    grpc_msg: Message = func(request_msg, metadata=[("req_id", req_id)])
                    return self._make_response(self.get_dict_from_msg(grpc_msg))

                return _route

    grpc_gateway_route: CustomerGrpcGatewayRoute = CustomerGrpcGatewayRoute(
        app,
        user_pb2_grpc.UserStub,
        social_pb2_grpc.BookSocialStub,
        manager_pb2_grpc.BookManagerStub,
        prefix="/api",
        title="Grpc",
        parse_msg_desc="by_mypy",
        gen_response_model_handle=gen_response_model_handle,
        make_response=_make_response,
    )
    grpc_gateway_route.init_channel(grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000")))
    set_app_attribute(app, "grpc_gateway_route", grpc_gateway_route)  # support unittest


def add_api_doc_route(app: Flask) -> None:
    """Split out to improve the speed of test cases"""
    add_doc_route(app, pin_code="6666", prefix="/", title="Pait Api Doc(private)")
    AddDocRoute(prefix="/api-doc", title="Pait Api Doc", app=app)


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
    app.add_url_rule("/api/login", view_func=login_route, methods=["POST"])
    app.add_url_rule("/api/user", view_func=get_user_route, methods=["GET"])
    app.add_url_rule("/api/raise-tip", view_func=raise_tip_route, methods=["POST"])
    app.add_url_rule("/api/post", view_func=post_route, methods=["POST"])
    app.add_url_rule("/api/depend", view_func=depend_route, methods=["POST"])
    app.add_url_rule("/api/pait-base-field/<age>", view_func=pait_base_field_route, methods=["POST"])
    app.add_url_rule("/api/field-default-factory", view_func=field_default_factory_route, methods=["POST"])
    app.add_url_rule("/api/same-alias", view_func=same_alias_route, methods=["GET"])
    app.add_url_rule("/api/mock/<age>", view_func=mock_route, methods=["GET"])
    app.add_url_rule("/api/pait-model", view_func=pait_model_route, methods=["POST"])
    app.add_url_rule("/api/cbv", view_func=CbvRoute.as_view("test_cbv"))
    app.add_url_rule("/api/check-param", view_func=check_param_route, methods=["GET"])
    app.add_url_rule("/api/text-resp", view_func=text_response_route, methods=["GET"])
    app.add_url_rule("/api/html-resp", view_func=html_response_route, methods=["GET"])
    app.add_url_rule("/api/file-resp", view_func=file_response_route, methods=["GET"])
    app.add_url_rule("/api/check-resp", view_func=check_response_route, methods=["GET"])
    app.add_url_rule("/api/check-json-plugin", view_func=check_json_plugin_route, methods=["GET"])
    app.add_url_rule("/api/cache-response", view_func=cache_response, methods=["GET"])
    app.add_url_rule("/api/cache-response-1", view_func=cache_response1, methods=["GET"])
    app.add_url_rule("/api/not-pait", view_func=not_pait_route, methods=["GET"])
    app.add_url_rule("/api/not-pait-cbv", view_func=NotPaitCbvRoute.as_view("NotPaitRoute"))
    app.add_url_rule("/api/check-json-plugin-1", view_func=check_json_plugin_route1, methods=["GET"])
    app.add_url_rule("/api/auto-complete-json-plugin", view_func=auto_complete_json_route, methods=["GET"])
    app.add_url_rule("/api/depend-contextmanager", view_func=depend_contextmanager_route, methods=["GET"])
    app.add_url_rule("/api/pre-depend-contextmanager", view_func=pre_depend_contextmanager_route, methods=["GET"])
    app.add_url_rule("/api/security/api-key", view_func=api_key_route, methods=["GET"])
    app.errorhandler(PaitBaseException)(api_exception)
    app.errorhandler(ValidationError)(api_exception)
    app.errorhandler(RuntimeError)(api_exception)
    load_app(app, auto_load_route=True)
    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.DEBUG
    )

    class ExtraModel(BaseModel):
        extra_a: str = Query.i(default="", description="Fields used to demonstrate the expansion module")
        extra_b: int = Query.i(default=0, description="Fields used to demonstrate the expansion module")

    config.init_config(
        apply_func_list=[
            apply_block_http_method_set({"HEAD", "OPTIONS"}),
            apply_extra_openapi_model(ExtraModel, match_rule=MatchRule(key="!tag", target="grpc")),
        ]
    )
    flask_app: Flask = create_app()
    add_grpc_gateway_route(flask_app)
    add_api_doc_route(flask_app)
    flask_app.run(port=8000, debug=True)
