import os
import sys
from typing import Any

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.common import tag
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.field import File
from pait.model.status import PaitStatus

file_pait: Pait = global_pait.create_sub_pait(
    group="file",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


@file_pait()
def stream_for_data_route(stream: Any = File.i()) -> JsonResponse:
    content = stream.read()
    return JsonResponse({"filename": stream.name, "length": len(content)})


@file_pait()
def multipart_route(stream: Any = File.i()) -> JsonResponse:
    content = stream.read()
    return JsonResponse({"filename": stream.name, "length": len(content)})


urlpatterns = [
    route_path("api/file/stream-for-data", stream_for_data_route, ["POST"], name="file_stream_for_data"),
    route_path("api/file/multipart", multipart_route, ["POST"], name="file_multipart"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.file_route_urlconf")
