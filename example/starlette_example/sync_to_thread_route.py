from starlette.responses import JSONResponse

from example.common import depend, tag
from example.common.response_model import FailRespModel, SimpleRespModel
from example.starlette_example.utils import create_app, global_pait
from pait.app.starlette import Pait
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
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


@sync_to_thread_pait(sync_to_thread=True)
def sync_body_route(
    uid: int = Body.t(),
    name: str = Body.t(),
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


@sync_to_thread_pait(sync_to_thread=True)
def sync_with_ctx_depend_route(
    uid: int = Depends.i(depend.sync_ctm_depend),
    name: str = Body.t(),
) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route("/api/sync-depend", sync_depend_route, methods=["POST"])
        app.add_route("/api/sync-body", sync_body_route, methods=["POST"])
        app.add_route("/api/sync-ctx-depend", sync_with_ctx_depend_route, methods=["POST"])
