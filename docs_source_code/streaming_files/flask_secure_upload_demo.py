import hashlib
import tempfile
from pathlib import Path

from flask import Flask

from pait.app.flask import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

app = Flask(__name__)
UPLOAD_DIR = Path(tempfile.gettempdir()) / "pait-streaming-upload"


def is_safe_filename(filename: str) -> bool:
    return bool(filename) and "/" not in filename and "\\" not in filename and ".." not in Path(filename).parts


@app.route("/api/secure-upload", methods=["POST"])
@pait()
def secure_upload(stream: SFDStream = StreamFile.i()) -> dict:
    filename = stream.filename()
    if not filename or not is_safe_filename(filename):
        return {"error": "Invalid filename"}

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

    return {
        "filename": filename,
        "size": total_size,
        "chunks_processed": chunk_count,
        "sha256": sha256.hexdigest(),
        "status": "uploaded successfully",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
