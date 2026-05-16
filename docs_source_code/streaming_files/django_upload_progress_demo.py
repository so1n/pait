import os
import sys

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.field import Header


@pait()
def upload_with_progress(
    expected_size: int = Header.i(default=0, alias="X-File-Size"),
    stream: SFDStream = StreamFile.i(),
) -> JsonResponse:
    total_size = 0
    chunk_count = 0

    for chunk in stream.stream():
        if not chunk:
            continue
        total_size += len(chunk)
        chunk_count += 1

    progress = round(total_size / expected_size * 100, 2) if expected_size else 100.0
    return JsonResponse(
        {
            "filename": stream.filename(),
            "total_size": total_size,
            "chunks_processed": chunk_count,
            "progress": min(progress, 100.0),
            "status": "completed",
        }
    )


urlpatterns = [route_path("api/upload-progress", upload_with_progress, ["POST"], name="upload_progress")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.streaming_files.django_upload_progress_demo_urlconf")
