import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile


class UploadHandler(RequestHandler):
    @pait()
    def post(self, stream: SFDStream = StreamFile.i()):
        """Upload a file using streaming form data (high performance)"""
        file_len = 0
        for chunk in stream.stream():
            file_len += len(chunk)

        self.write({"filename": stream.filename(), "length": file_len})


def make_app():
    return tornado.web.Application(
        [
            (r"/api/upload", UploadHandler),
        ]
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
