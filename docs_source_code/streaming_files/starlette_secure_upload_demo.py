import hashlib
import tempfile
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

UPLOAD_DIR = Path(tempfile.gettempdir()) / "pait-streaming-upload"


def is_safe_filename(filename: str) -> bool:
    return bool(filename) and "/" not in filename and "\\" not in filename and ".." not in Path(filename).parts


@pait()
async def secure_upload(stream: SFDStream = StreamFile.i()) -> JSONResponse:
    filename = await stream.filename()
    if not filename or not is_safe_filename(filename):
        return JSONResponse({"error": "Invalid filename"}, status_code=400)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / filename
    sha256 = hashlib.sha256()
    total_size = 0
    chunk_count = 0

    with file_path.open("wb") as file:
        async for chunk in stream.stream():
            if not chunk:
                continue
            file.write(chunk)
            sha256.update(chunk)
            total_size += len(chunk)
            chunk_count += 1

    return JSONResponse(
        {
            "filename": filename,
            "size": total_size,
            "chunks_processed": chunk_count,
            "sha256": sha256.hexdigest(),
            "status": "uploaded successfully",
        }
    )


app = Starlette(routes=[Route("/api/secure-upload", secure_upload, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
