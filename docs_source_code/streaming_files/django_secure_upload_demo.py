import hashlib
import os
import sys
import tempfile
from pathlib import Path

if not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.http import JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

UPLOAD_DIR = Path(tempfile.gettempdir()) / "pait-streaming-upload"


def is_safe_filename(filename: str) -> bool:
    return bool(filename) and "/" not in filename and "\\" not in filename and ".." not in Path(filename).parts


@pait()
def secure_upload(stream: SFDStream = StreamFile.i()) -> JsonResponse:
    filename = stream.filename()
    if not filename or not is_safe_filename(filename):
        return JsonResponse({"error": "Invalid filename"})

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / filename
    sha256 = hashlib.sha256()
    total_size = 0
    chunk_count = 0

    with file_path.open("wb") as file:
        for chunk in stream.stream():
            if not chunk:
                continue
            file.write(chunk)
            sha256.update(chunk)
            total_size += len(chunk)
            chunk_count += 1

    return JsonResponse(
        {
            "filename": filename,
            "size": total_size,
            "chunks_processed": chunk_count,
            "sha256": sha256.hexdigest(),
            "status": "uploaded successfully",
        }
    )


urlpatterns = [route_path("api/secure-upload", secure_upload, ["POST"], name="secure_upload")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "docs_source_code.streaming_files.django_secure_upload_demo_urlconf")
