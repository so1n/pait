import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.field import Header


@pait()
async def upload_with_progress(
    expected_size: int = Header.i(default=0, alias="X-File-Size"),
    stream: SFDStream = StreamFile.i(),
) -> JSONResponse:
    total_size = 0
    chunk_count = 0

    async for chunk in stream.stream():
        if not chunk:
            continue
        total_size += len(chunk)
        chunk_count += 1

    progress = round(total_size / expected_size * 100, 2) if expected_size else 100.0
    return JSONResponse(
        {
            "filename": await stream.filename(),
            "total_size": total_size,
            "chunks_processed": chunk_count,
            "progress": min(progress, 100.0),
            "status": "completed",
        }
    )


app = Starlette(routes=[Route("/api/upload-progress", upload_with_progress, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
