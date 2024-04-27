from example.common import depend, tag
from example.common.response_model import FailRespModel, SimpleRespModel
from example.tornado_example.utils import MyHandler, create_app, global_pait
from pait.app.tornado import Pait
from pait.field import Body, Depends
from pait.model.status import PaitStatus

sync_to_thread_pait: Pait = global_pait.create_sub_pait(
    group="sync-to-thread",
    status=PaitStatus.release,
    tag=(tag.sync_to_thread_tag,),
    response_model_list=[SimpleRespModel, FailRespModel],
)


class SyncDependHandler(MyHandler):

    @sync_to_thread_pait(sync_to_thread=True)
    def post(
        self,
        uid: int = Depends.i(depend.sync_depend),
        name: str = Depends.i(depend.async_depend),
    ) -> None:
        return self.write({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


class SyncToThreadBodyHandler(MyHandler):

    @sync_to_thread_pait(sync_to_thread=True)
    def post(
        self,
        uid: int = Body.t(),
        name: str = Body.t(),
    ) -> None:
        return self.write({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


class SyncWithCtxDependHandler(MyHandler):

    @sync_to_thread_pait(sync_to_thread=True)
    def post(
        self,
        uid: int = Depends.i(depend.sync_ctm_depend),
        name: str = Body.t(),
    ) -> None:
        return self.write({"code": 0, "msg": "", "data": {"uid": uid, "name": name}})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route(
            [
                (r"/api/sync-depend", SyncDependHandler),
                (r"/api/sync-body", SyncToThreadBodyHandler),
                (r"/api/sync-ctx-depend", SyncWithCtxDependHandler),
            ]
        )
