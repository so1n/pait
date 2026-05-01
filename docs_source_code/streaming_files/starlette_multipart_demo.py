import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.extra.field.stream.by_multipart import AsyncStream as MultipartStream
from pait.extra.field.stream.request_resource import StreamFile


@pait()
async def upload_file(stream: MultipartStream = StreamFile.i()) -> JSONResponse:
    """Upload a file using multipart streaming"""
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)

    return JSONResponse(
        {
            "filename": await stream.filename(),
            "length": file_len,
            "content_type": (await stream.info()).content_type if await stream.info() else None,
        }
    )


app = Starlette(routes=[Route("/api/upload", upload_file, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
