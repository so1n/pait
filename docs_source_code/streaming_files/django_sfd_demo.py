import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile


@pait()
def upload_file(stream: SFDStream = StreamFile.i()) -> JsonResponse:
    """Upload a file using streaming form data (high performance)"""
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)

    return JsonResponse({"filename": stream.filename(), "length": file_len})


urlpatterns = [route_path("api/upload", upload_file, ["POST"], name="upload")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.streaming_files.django_sfd_demo_urlconf")
