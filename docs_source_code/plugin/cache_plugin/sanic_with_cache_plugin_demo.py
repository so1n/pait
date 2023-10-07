import time
from typing import Any

from redis.asyncio import Redis  # type: ignore
from sanic import Sanic, response

from pait.app.sanic import pait
from pait.app.sanic.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
async def demo(
    key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()
) -> response.HTTPResponse:
    return response.html(str(time.time()), 200)


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods=["GET"])


def before_start(*args: Any, **kwargs: Any) -> None:
    CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))


app.before_server_start(before_start)


if __name__ == "__main__":
    app.run(port=8000)
