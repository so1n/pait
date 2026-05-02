from sanic import Sanic
from sanic.response import json

from pait.app.sanic import pait
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.field import Header


@pait()
async def upload_with_progress(
    expected_size: int = Header.i(default=0, alias="X-File-Size"),
    stream: SFDStream = StreamFile.i(),
):
    total_size = 0
    chunk_count = 0

    async for chunk in stream.stream():
        if not chunk:
            continue
        total_size += len(chunk)
        chunk_count += 1

    progress = round(total_size / expected_size * 100, 2) if expected_size else 100.0
    return json(
        {
            "filename": await stream.filename(),
            "total_size": total_size,
            "chunks_processed": chunk_count,
            "progress": min(progress, 100.0),
            "status": "completed",
        }
    )


app = Sanic(name="streaming_upload_progress_demo", configure_logging=False)
app.add_route(upload_with_progress, "/api/upload-progress", methods=["POST"], stream=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
