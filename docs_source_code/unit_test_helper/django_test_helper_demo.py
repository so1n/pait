import os
import sys
from functools import partial

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse
from django.test import Client

from example.django_example.utils import configure_urlpatterns, route_path
from pait.app.django import TestHelper, load_app, pait
from pait.field import Json


@pait()
def demo_post(
    uid: int = Json.t(description="user id", gt=10, lt=1000),
    username: str = Json.t(description="user name", min_length=2, max_length=4),
) -> JsonResponse:
    return JsonResponse({"uid": uid, "user_name": username})


urlpatterns = [route_path("api", demo_post, ["POST"], name="demo")]


def test_demo_route() -> None:
    configure_urlpatterns(urlpatterns, "docs_source_code.unit_test_helper.django_test_helper_demo_urlconf")
    helper = TestHelper(
        Client(),
        demo_post,
        load_app=partial(load_app, overwrite_already_exists_data=True),
        body_dict={"uid": 123, "username": "appl"},
    )
    assert helper.json(method="POST") == {"uid": 123, "user_name": "appl"}
