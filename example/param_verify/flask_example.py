from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, Request
from flask.views import MethodView
from pydantic import ValidationError

from example.param_verify.model import (
    FailRespModel,
    SexEnum,
    TestPaitModel,
    UserModel,
    UserOtherModel,
    UserSuccessRespModel,
    UserSuccessRespModel2,
    demo_depend,
)
from pait.app.flask import add_doc_route, pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Cookie, Depends, File, Form, Header, MultiForm, MultiQuery, Path, Query
from pait.g import config
from pait.model.status import PaitStatus


def api_exception(exc: Exception) -> Dict[str, str]:
    return {"exc": str(exc)}


@pait(
    author=("so1n",),
    desc="test pait raise tip",
    status=PaitStatus.abandoned,
    tag=("test",),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
def test_raise_tip(
    model: UserModel = Body.i(),
    other_model: UserOtherModel = Body.i(),
    content__type: str = Header.i(description="Content-Type"),  # in flask, Content-Type's key is content_type
) -> dict:
    """Test Method: error tip"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content__type})
    return {"code": 0, "msg": "", "data": return_dict}


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "post"),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
def test_post(
    model: UserModel = Body.i(),
    other_model: UserOtherModel = Body.i(),
    sex: SexEnum = Body.i(description="sex"),
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> dict:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict["sex"] = sex.value
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return {"code": 0, "msg": "", "data": return_dict}


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "depend"),
    response_model_list=[UserSuccessRespModel, FailRespModel],
)
def demo_get2test_depend(
    request: Request,
    model: UserModel = Query.i(),
    depend_tuple: Tuple[str, int] = Depends.i(demo_depend),
) -> dict:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return_dict = model.dict()
    return_dict.update({"user_agent": depend_tuple[0], "age": depend_tuple[1]})
    return {"code": 0, "msg": "", "data": return_dict}


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
)
def test_other_field(
    upload_file: Any = File.i(description="upload file"),
    a: str = Form.i(description="form data"),
    b: str = Form.i(description="form data"),
    c: List[str] = MultiForm.i(description="form data"),
    cookie: dict = Cookie.i(raw_return=True, description="cookie"),
) -> dict:
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
        },
    }


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
    at_most_one_of_list=[["user_name", "alias_user_name"]],
    required_by={"birthday": ["alias_user_name"]},
)
def test_check_param(
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


@pait(
    author=("so1n",),
    group="user",
    status=PaitStatus.release,
    tag=("user", "get"),
    response_model_list=[UserSuccessRespModel2, FailRespModel],
)
def test_pait(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    multi_user_name: List[str] = MultiQuery.i(description="user name", min_length=2, max_length=4),
    age: int = Path.i(description="age", gt=1, lt=100),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test Field"""
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


@pait(
    author=("so1n",), status=PaitStatus.test, tag=("test",), response_model_list=[UserSuccessRespModel, FailRespModel]
)
def test_model(test_model: TestPaitModel) -> dict:
    """Test Field"""
    return {"code": 0, "msg": "", "data": test_model.dict()}


class TestCbv(MethodView):
    user_agent: str = Header.i(alias="user-agent", description="ua")  # remove key will raise error

    @pait(
        author=("so1n",),
        group="user",
        status=PaitStatus.release,
        tag=("user", "get"),
        response_model_list=[UserSuccessRespModel2, FailRespModel],
    )
    def get(
        self,
        uid: int = Query.i(description="user id", gt=10, lt=1000),
        user_name: str = Query.i(description="user name", min_length=2, max_length=4),
        email: Optional[str] = Query.i(default="example@xxx.com", description="email"),
        model: UserOtherModel = Query.i(),
    ) -> dict:
        """Text Pydantic Model and Field"""
        return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": model.age}
        return {"code": 0, "msg": "", "data": return_dict}

    @pait(
        author=("so1n",),
        desc="test cbv post method",
        group="user",
        tag=("user", "post"),
        status=PaitStatus.release,
        response_model_list=[UserSuccessRespModel, FailRespModel],
    )
    def post(
        self,
        model: UserModel = Body.i(),
        other_model: UserOtherModel = Body.i(),
    ) -> dict:
        return_dict = model.dict()
        return_dict.update(other_model.dict())
        return_dict.update({"user_agent": self.user_agent})
        return {"code": 0, "msg": "", "data": return_dict}


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    add_doc_route(app)
    app.add_url_rule("/api/raise_tip", view_func=test_raise_tip, methods=["POST"])
    app.add_url_rule("/api/post", view_func=test_post, methods=["POST"])
    app.add_url_rule("/api/depend", view_func=demo_get2test_depend, methods=["POST"])
    app.add_url_rule("/api/other_field", view_func=test_other_field, methods=["POST"])
    app.add_url_rule("/api/get/<age>", view_func=test_pait, methods=["GET"])
    app.add_url_rule("/api/pait_model", view_func=test_model, methods=["POST"])
    app.add_url_rule("/api/cbv", view_func=TestCbv.as_view("test_cbv"))
    app.add_url_rule("/api/check_param", view_func=test_check_param, methods=["GET"])
    app.errorhandler(PaitBaseException)(api_exception)
    app.errorhandler(ValidationError)(api_exception)
    return app


if __name__ == "__main__":
    config.init_config(block_http_method_set={"HEAD", "OPTIONS"})
    create_app().run(port=8000, debug=True)
