from sanic import Sanic
from sanic.response import json

from pait.app.sanic import pait
from pait.extra.field.stream.by_multipart import AsyncStream as MultipartStream
from pait.extra.field.stream.request_resource import StreamFile

app = Sanic("streaming_demo")


@app.route("/api/upload", methods=["POST"], stream=True)
@pait()
async def upload_file(stream: MultipartStream = StreamFile.i()):
    """Upload a file using multipart streaming"""
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)

    return json(
        {
            "filename": await stream.filename(),
            "length": file_len,
            "content_type": (await stream.info()).content_type if await stream.info() else None,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
