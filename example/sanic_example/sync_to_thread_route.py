from sanic import response

from example.common import depend, tag
from example.common.response_model import FailRespModel, SimpleRespModel
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
from pait.field import Body, Depends
from pait.model.status import PaitStatus

sync_to_thread_pait: Pait = global_pait.create_sub_pait(
    group="sync-to-thread",
    status=PaitStatus.release,
    tag=(tag.sync_to_thread_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


@sync_to_thread_pait(sync_to_thread=True)
def sync_depend_route(
    uid: int = Depends.i(depend.sync_depend),
    name: str = Depends.i(depend.async_depend),
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


@sync_to_thread_pait(sync_to_thread=True)
def sync_body_route(
    uid: int = Body.t(),
    name: str = Body.t(),
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


@sync_to_thread_pait(sync_to_thread=True)
def sync_with_ctx_depend_route(
    uid: int = Depends.i(depend.sync_ctm_depend),
    name: str = Body.t(),
) -> response.HTTPResponse:
    return response.json({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = "1"
    with create_app(__name__) as app:
        app.add_route(sync_depend_route, "/api/sync-depend", methods={"POST"})
        app.add_route(sync_body_route, "/api/sync-body", methods={"POST"})
        app.add_route(sync_with_ctx_depend_route, "/api/sync-ctx-depend", methods={"POST"})
