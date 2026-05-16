import os
import sys
import time

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import HttpResponse
from redis import Redis  # type: ignore

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.app.django.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[
        CacheResponsePlugin.build(
            redis=Redis(decode_responses=True),
            cache_time=10,
            enable_cache_name_merge_param=True,
        )
    ],
)
def demo(key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()) -> HttpResponse:
    return HttpResponse(str(time.time()))


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.plugin.cache_plugin.django_with_cache_plugin_demo_urlconf")
