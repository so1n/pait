import time

from flask import Flask, Response, make_response
from redis import Redis  # type: ignore

from pait.app.flask import pait
from pait.app.flask.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
def demo(key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()) -> Response:
    return make_response(str(time.time()), 200)


app = Flask("demo")
CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
