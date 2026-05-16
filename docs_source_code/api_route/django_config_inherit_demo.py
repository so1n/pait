import os
import sys
from typing import Any, List

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import run_urlpatterns
from pait.app.django import APIRoute
from pait.g import get_ctx
from pait.model.tag import Tag

api_tag = Tag("api-route-api")
users_tag = Tag("api-route-users")

parent_route = APIRoute(path="/api", group="main", append_tag=(api_tag,))
child_route = APIRoute(path="/users", tag=(users_tag,))


@child_route.get("/profile")
def get_profile() -> JsonResponse:
    core_model = get_ctx().pait_core_model
    return JsonResponse({"group": core_model.group, "tags": [tag.name for tag in core_model.tag]})


parent_route.include_sub_route(child_route)

urlpatterns: List[Any] = []
parent_route.inject(urlpatterns)


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.api_route.django_config_inherit_demo_urlconf")
