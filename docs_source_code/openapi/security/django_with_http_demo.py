import os
import sys
from typing import Optional

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.app.django.security import http
from pait.field import Depends
from pait.openapi.doc_route import AddDocRoute

http_basic: http.HTTPBasic = http.HTTPBasic()


def get_user_name(credentials: Optional[http.HTTPBasicCredentials] = Depends.i(http_basic)) -> str:
    if not credentials or credentials.username != credentials.password:
        raise http_basic.not_authorization_exc
    return credentials.username


@pait()
def get_user_name_by_http_basic_credentials(user_name: str = Depends.t(get_user_name)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": user_name})


http_bear: http.HTTPBearer = http.HTTPBearer(verify_callable=lambda x: "http" in x)


@pait()
def get_user_name_by_http_bearer(credentials: Optional[str] = Depends.i(http_bear)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": credentials})


http_digest: http.HTTPDigest = http.HTTPDigest(verify_callable=lambda x: "http" in x)


@pait()
def get_user_name_by_http_digest(credentials: Optional[str] = Depends.i(http_digest)) -> JsonResponse:
    return JsonResponse({"code": 0, "msg": "", "data": credentials})


urlpatterns = [
    route_path(
        "api/user-name-by-http-basic-credentials",
        get_user_name_by_http_basic_credentials,
        ["GET"],
        name="http_basic",
    ),
    route_path("api/user-name-by-http-bearer", get_user_name_by_http_bearer, ["GET"], name="http_bearer"),
    route_path("api/user-name-by-http-digest", get_user_name_by_http_digest, ["GET"], name="http_digest"),
]
AddDocRoute(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.openapi.security.django_with_http_demo_urlconf")
