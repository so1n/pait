import os
import sys
from typing import Tuple

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import HttpRequest, JsonResponse

from example.common import depend, tag
from example.common.request_model import UserModel
from example.common.response_model import FailRespModel, SimpleRespModel
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.field import Depends, Query
from pait.model.status import PaitStatus

depend_pait: Pait = global_pait.create_sub_pait(
    group="depend",
    status=PaitStatus.release,
    tag=(tag.depend_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


@depend_pait(append_tag=(tag.user_tag,))
def depend_route(
    request: HttpRequest,
    depend_tuple: Tuple[str, int] = Depends.i(depend.demo_depend),
    user_model: UserModel = Depends.i(depend.GetUserDepend),
) -> JsonResponse:
    assert request is not None, "Not found request"
    return JsonResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "user_agent": depend_tuple[0],
                "age": depend_tuple[1],
                "user_info": user_model.dict(),
            },
        }
    )


@depend_pait(append_tag=(tag.user_tag,), pre_depend_list=[depend.CheckTokenDepend])
def pre_depend_route() -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": {}})


@depend_pait(status=PaitStatus.test)
def depend_contextmanager_route(
    uid: int = Depends.i(depend.context_depend), is_raise: bool = Query.i(default=False)
) -> JsonResponse:
    if is_raise:
        raise RuntimeError("test")
    return JsonResponse({"code": 0, "msg": str(uid)})


@depend_pait(status=PaitStatus.test, pre_depend_list=[depend.context_depend])
def pre_depend_contextmanager_route(is_raise: bool = Query.i(default=False)) -> JsonResponse:
    if is_raise:
        raise RuntimeError()
    return JsonResponse({"code": 0, "msg": ""})


urlpatterns = [
    route_path("api/depend", depend_route, ["POST"], name="depend"),
    route_path("api/pre-depend", pre_depend_route, ["POST"], name="pre_depend"),
    route_path("api/depend-contextmanager", depend_contextmanager_route, ["GET"], name="depend_contextmanager"),
    route_path(
        "api/pre-depend-contextmanager",
        pre_depend_contextmanager_route,
        ["GET"],
        name="pre_depend_contextmanager",
    ),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.depend_route_urlconf")
