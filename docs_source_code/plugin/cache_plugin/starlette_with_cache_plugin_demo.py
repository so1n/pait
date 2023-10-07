import time
from typing import Any

from redis.asyncio import Redis  # type: ignore
from starlette.applications import Starlette
from starlette.responses import HTMLResponse

from pait.app.starlette import pait
from pait.app.starlette.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
async def demo(key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()) -> HTMLResponse:
    return HTMLResponse(str(time.time()), 200)


app = Starlette()
app.add_route("/api/demo", demo, methods=["GET"])


def before_start(*args: Any, **kwargs: Any) -> None:
    CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))


app.add_event_handler("startup", before_start)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
