from flask import Flask

from pait.app.flask import pait
from pait.extra.field.stream.by_streaming_form_data import Stream as SFDStream
from pait.extra.field.stream.request_resource import StreamFile

app = Flask(__name__)


@app.route("/api/upload", methods=["POST"])
@pait()
def upload_file(stream: SFDStream = StreamFile.i()) -> dict:
    """Upload a file using streaming form data (high performance)"""
    file_len = 0
    for chunk in stream.stream():
        file_len += len(chunk)

    return {"filename": stream.filename(), "length": file_len}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
