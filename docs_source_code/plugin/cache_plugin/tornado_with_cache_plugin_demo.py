import time

from redis.asyncio import Redis  # type: ignore
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from pait.app.tornado import pait
from pait.app.tornado.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel


class DemoHandler(RequestHandler):
    @pait(
        response_model_list=[HtmlResponseModel],
        post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
    )
    async def get(self, key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()) -> None:
        self.write(str(time.time()))


app: Application = Application([(r"/api/demo", DemoHandler)])
CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))


if __name__ == "__main__":
    app.listen(8000)
    IOLoop.instance().start()
