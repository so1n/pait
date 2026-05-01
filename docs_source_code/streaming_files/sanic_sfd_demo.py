from sanic import Sanic
from sanic.response import json

from pait.app.sanic import pait
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

app = Sanic("streaming_demo")


@app.route("/api/upload", methods=["POST"], stream=True)
@pait()
async def upload_file(stream: SFDStream = StreamFile.i()):
    """Upload a file using streaming form data (high performance)"""
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)

    return json({"filename": await stream.filename(), "length": file_len})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
