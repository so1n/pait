import os
import sys
from typing import Optional

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait import field
from pait.app.django import pait
from pait.plugin.at_most_one_of import AtMostOneOfPlugin


@pait(post_plugin_list=[AtMostOneOfPlugin.build(at_most_one_of_list=[["email", "user_name"]])])
def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None),
) -> JsonResponse:
    return JsonResponse({"uid": uid, "user_name": user_name, "email": email})


urlpatterns = [route_path("api/demo", demo, ["GET"], name="demo")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.plugin.param_plugin.django_with_at_most_one_of_plugin_demo_urlconf")
