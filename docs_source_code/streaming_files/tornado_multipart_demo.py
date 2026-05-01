import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import pait
from pait.extra.field.stream.by_multipart import Stream as MultipartStream
from pait.extra.field.stream.request_resource import StreamFile


class UploadHandler(RequestHandler):
    @pait()
    def post(self, stream: MultipartStream = StreamFile.i()):
        """Upload a file using multipart streaming"""
        file_len = 0
        for chunk in stream.stream():
            file_len += len(chunk)

        self.write(
            {
                "filename": stream.filename(),
                "length": file_len,
                "content_type": stream.info().content_type if stream.info() else None,
            }
        )


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
