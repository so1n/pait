import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.common import tag
from example.django_example.utils import global_pait, route_path, run_urlpatterns
from pait.app.django import Pait
from pait.extra.field.stream.by_multipart import Stream as MultipartStream
from pait.extra.field.stream.by_streaming_form_data import Stream as SFAStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.model.status import PaitStatus

file_pait: Pait = global_pait.create_sub_pait(
    group="file",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


@file_pait()
def stream_for_data_route(stream: SFAStream = StreamFile.i()) -> JsonResponse:
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)
    return JsonResponse({"filename": stream.filename(), "length": file_len})


@file_pait()
def multipart_route(stream: MultipartStream = StreamFile.i()) -> JsonResponse:
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)
    return JsonResponse({"filename": stream.filename(), "length": file_len})


urlpatterns = [
    route_path("api/file/stream-for-data", stream_for_data_route, ["POST"], name="file_stream_for_data"),
    route_path("api/file/multipart", multipart_route, ["POST"], name="file_multipart"),
]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.file_route_urlconf")
