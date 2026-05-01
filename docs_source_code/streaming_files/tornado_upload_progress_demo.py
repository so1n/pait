import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.field import Header


class UploadProgressHandler(RequestHandler):
    @pait()
    def post(
        self,
        expected_size: int = Header.i(default=0, alias="X-File-Size"),
        stream: SFDStream = StreamFile.i(),
    ) -> None:
        total_size = 0
        chunk_count = 0

        for chunk in stream.stream():
            if not chunk:
                continue
            total_size += len(chunk)
            chunk_count += 1

        progress = round(total_size / expected_size * 100, 2) if expected_size else 100.0
        self.write(
            {
                "filename": stream.filename(),
                "total_size": total_size,
                "chunks_processed": chunk_count,
                "progress": min(progress, 100.0),
                "status": "completed",
            }
        )


def make_app():
    return tornado.web.Application([(r"/api/upload-progress", UploadProgressHandler)])


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
