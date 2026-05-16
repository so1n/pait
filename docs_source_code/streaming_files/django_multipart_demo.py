import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.extra.field.stream.by_multipart import Stream as MultipartStream
from pait.extra.field.stream.request_resource import StreamFile


@pait()
def upload_file(stream: MultipartStream = StreamFile.i()) -> JsonResponse:
    """Upload a file using multipart streaming"""
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)

    info = stream.info()
    return JsonResponse(
        {
            "filename": stream.filename(),
            "length": file_len,
            "content_type": info.content_type if info else None,
        }
    )


urlpatterns = [route_path("api/upload", upload_file, ["POST"], name="upload")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.streaming_files.django_multipart_demo_urlconf")
