import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.app.django.security import api_key
from pait.field import Cookie, Depends, Header, Query

cookie_api_key = api_key.APIKey(name="token", field=Cookie(openapi_include=False), verify_api_key_callable=bool)
header_api_key = api_key.APIKey(name="token", field=Header(openapi_include=False), verify_api_key_callable=bool)
query_api_key = api_key.APIKey(name="token", field=Query(openapi_include=False), verify_api_key_callable=bool)


@pait()
def api_key_cookie_route(token: str = Depends.t(cookie_api_key)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": token})


@pait()
def api_key_header_route(token: str = Depends.t(header_api_key)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": token})


@pait()
def api_key_query_route(token: str = Depends.t(query_api_key)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": token})


urlpatterns = [
    route_path("api/cookie", api_key_cookie_route, ["GET"], name="api_key_cookie"),
    route_path("api/header", api_key_header_route, ["GET"], name="api_key_header"),
    route_path("api/query", api_key_query_route, ["GET"], name="api_key_query"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.openapi.security.django_with_apikey_demo_urlconf")
