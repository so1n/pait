from typing import Tuple

from flask import Request

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import FailRespModel, SimpleRespModel
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.field import Depends, Query
from pait.model import PaitStatus

depend_pait: Pait = global_pait.create_sub_pait(
    group="depend",
    status=PaitStatus.release,
    tag=(tag.depend_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


@depend_pait(append_tag=(tag.user_tag,))
def depend_route(
    request: Request,
    depend_tuple: Tuple[str, int] = Depends.i(depend.demo_depend),
    user_model: UserModel = Depends.i(depend.GetUserDepend()),
) -> dict:
    """Testing depend and using request parameters"""
    assert request is not None, "Not found request"
    return {
        "code": 0,
        "msg": "",
        "data": {"user_agent": depend_tuple[0], "age": depend_tuple[1], "user_info": user_model.dict()},
    }


@depend_pait(status=PaitStatus.test)
def depend_contextmanager_route(
    uid: int = Depends.i(depend.context_depend), is_raise: bool = Query.i(default=False)
) -> dict:
    if is_raise:
        raise RuntimeError("test")
    return {"code": 0, "msg": uid}


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.context_depend])
def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> dict:
    if is_raise:
        raise RuntimeError()
    return {"code": 0, "msg": ""}


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/depend", view_func=depend_route, methods=["POST"])
        app.add_url_rule("/api/depend-contextmanager", view_func=depend_contextmanager_route, methods=["GET"])
        app.add_url_rule("/api/pre-depend-contextmanager", view_func=pre_depend_contextmanager_route, methods=["GET"])
