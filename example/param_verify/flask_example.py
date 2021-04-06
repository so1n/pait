from typing import Dict, Optional

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
from pait.app.flask import pait
from pait.exceptions import PaitBaseException
from pait.field import Body, Depends, Header, Path, Query
from pait.model import PaitStatus

app = Flask(__name__)


def api_exception(exc: Exception) -> Dict[str, str]:
    return {"exc": str(exc)}


@app.route("/api/raise_tip", methods=["POST"])
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
    return {
        "code": 0,
        "msg": "",
        "data": return_dict
    }


@app.route("/api/post", methods=["POST"])
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
    content_type: str = Header.i(alias="Content-Type", description="Content-Type"),
) -> dict:
    """Test Method:Post Pydantic Model"""
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"content_type": content_type})
    return {
        "code": 0,
        "msg": "",
        "data": return_dict
    }


@app.route("/api/depend", methods=["GET"])
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
    other_model: UserOtherModel = Query.i(),
    user_agent: str = Depends.i(demo_depend),
) -> dict:
    """Test Method:Post request, Pydantic Model"""
    assert request is not None, "Not found request"
    return_dict = model.dict()
    return_dict.update(other_model.dict())
    return_dict.update({"user_agent": user_agent})
    return {
        "code": 0,
        "msg": "",
        "data": return_dict
    }


@app.route("/api/get/<age>", methods=["GET"])
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
    age: int = Path.i(),
    sex: SexEnum = Query.i(description="sex"),
) -> dict:
    """Test Field"""
    return_dict = {"uid": uid, "user_name": user_name, "email": email, "age": age, "sex": sex.value}
    return {
        "code": 0,
        "msg": "",
        "data": return_dict
    }


@app.route("/api/pait_model", methods=["GET"])
@pait(
    author=("so1n",),
    status=PaitStatus.test,
    tag=("test",),
    response_model_list=[UserSuccessRespModel, FailRespModel]
)
def test_model(test_model: TestPaitModel) -> dict:
    """Test Field"""
    return {
        "code": 0,
        "msg": "",
        "data": test_model.dict()
    }


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
        return {
            "code": 0,
            "msg": "",
            "data": return_dict
        }

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
        return {
            "code": 0,
            "msg": "",
            "data": return_dict
        }


app.add_url_rule("/api/cbv", view_func=TestCbv.as_view("test_cbv"))
app.errorhandler(PaitBaseException)(api_exception)
app.errorhandler(ValidationError)(api_exception)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
