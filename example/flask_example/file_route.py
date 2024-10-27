from example.common import tag
from example.flask_example.utils import create_app, global_pait
from pait.app.flask import Pait
from pait.extra.field.stream.by_multipart import Stream as MultipartStream
from pait.extra.field.stream.by_streaming_form_data import Stream as SFAStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.model.status import PaitStatus

file_pait: Pait = global_pait.create_sub_pait(
    group="file",
    status=PaitStatus.release,
    tag=(tag.field_tag,),
)

aaa = StreamFile.t(SFAStream)


@file_pait()
def stream_for_data_route(stream: SFAStream = StreamFile.i()) -> dict:
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)
    return {"filename": stream.filename(), "length": file_len}


@file_pait()
def multipart_route(stream: MultipartStream = StreamFile.i()) -> dict:
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)
    return {"filename": stream.filename(), "length": file_len}


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_url_rule("/api/file/stream-for-data", view_func=stream_for_data_route, methods=["POST"])
        app.add_url_rule("/api/file/multipart", view_func=multipart_route, methods=["POST"])
