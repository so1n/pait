import hashlib
import tempfile
from pathlib import Path

import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler

from pait.app.tornado import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

UPLOAD_DIR = Path(tempfile.gettempdir()) / "pait-streaming-upload"


def is_safe_filename(filename: str) -> bool:
    return bool(filename) and "/" not in filename and "\\" not in filename and ".." not in Path(filename).parts


class SecureUploadHandler(RequestHandler):
    @pait()
    def post(self, stream: SFDStream = StreamFile.i()) -> None:
        filename = stream.filename()
        if not filename or not is_safe_filename(filename):
            self.set_status(400)
            self.write({"error": "Invalid filename"})
            return

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / filename
        sha256 = hashlib.sha256()
        total_size = 0
        chunk_count = 0

        with file_path.open("wb") as file:
            for chunk in stream.stream():
                if not chunk:
                    continue
                file.write(chunk)
                sha256.update(chunk)
                total_size += len(chunk)
                chunk_count += 1

        self.write(
            {
                "filename": filename,
                "size": total_size,
                "chunks_processed": chunk_count,
                "sha256": sha256.hexdigest(),
                "status": "uploaded successfully",
            }
        )


def make_app():
    return tornado.web.Application([(r"/api/secure-upload", SecureUploadHandler)])


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
