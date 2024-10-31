from starlette.responses import JSONResponse

from example.common import tag
from example.starlette_example.utils import create_app, global_pait
from pait.app.starlette import Pait
from pait.extra.field.stream.by_multipart import AsyncStream as MultipartStream
from pait.extra.field.stream.by_streaming_form_data import AsyncStream as SFAStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.model.status import PaitStatus

file_pait: Pait = global_pait.create_sub_pait(
    group="file",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)


@file_pait()
async def stream_for_data_route(stream: SFAStream = StreamFile.i()) -> JSONResponse:
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)
    return JSONResponse({"filename": await stream.filename(), "length": file_len})


@file_pait()
async def multipart_route(stream: MultipartStream = StreamFile.i()) -> JSONResponse:
    file_len = 0
    async for chunk in stream.stream():
        file_len += len(chunk)
    return JSONResponse({"filename": await stream.filename(), "length": file_len})


if __name__ == "__main__":
    with create_app() as app:
        app.add_route("/api/file/stream-for-data", stream_for_data_route, methods=["POST"])
        app.add_route("/api/file/multipart", multipart_route, methods=["POST"])