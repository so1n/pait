import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from example.django_example.utils import run_urlpatterns
from pait.app.base.simple_route import SimpleRoute
from pait.app.django import add_multi_simple_route, add_simple_route, pait
from pait.model.response import HtmlResponseModel, JsonResponseModel, TextResponseModel


@pait(response_model_list=[JsonResponseModel])
def json_route() -> dict:
    return {"name": "json"}


@pait(response_model_list=[TextResponseModel])
def text_route() -> str:
    return "text"


@pait(response_model_list=[HtmlResponseModel])
def html_route() -> str:
    return "<h1>html</h1>"


urlpatterns: List[Any] = []
add_simple_route(urlpatterns, SimpleRoute(methods=["GET"], url="/api/json", route=json_route))
add_multi_simple_route(
    urlpatterns,
    SimpleRoute(methods=["GET"], url="/text", route=text_route),
    SimpleRoute(methods=["GET"], url="/html", route=html_route),
    prefix="/api",
)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.other.django_with_simple_route_demo_urlconf")
