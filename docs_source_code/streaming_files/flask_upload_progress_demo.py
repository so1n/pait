from flask import Flask

from pait.app.flask import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile
from pait.field import Header

app = Flask(__name__)


@app.route("/api/upload-progress", methods=["POST"])
@pait()
def upload_with_progress(
    expected_size: int = Header.i(default=0, alias="X-File-Size"),
    stream: SFDStream = StreamFile.i(),
) -> dict:
    total_size = 0
    chunk_count = 0

    for chunk in stream.stream():
        if not chunk:
            continue
        total_size += len(chunk)
        chunk_count += 1

    progress = round(total_size / expected_size * 100, 2) if expected_size else 100.0
    return {
        "filename": stream.filename(),
        "total_size": total_size,
        "chunks_processed": chunk_count,
        "progress": min(progress, 100.0),
        "status": "completed",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
