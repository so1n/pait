import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile


@pait()
async def upload_file(stream: SFDStream = StreamFile.i()) -> JSONResponse:
    """Upload a file using streaming form data (high performance)"""
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)

    return JSONResponse({"filename": await stream.filename(), "length": file_len})


app = Starlette(routes=[Route("/api/upload", upload_file, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
