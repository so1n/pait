import hashlib
from typing import Tuple

CONTENT = b"hello pait"
FILENAME = "pait-upload-demo.txt"
BOUNDARY = "----pait-streaming-test-boundary"


def build_multipart_body(
    field_name: str = "stream", filename: str = FILENAME, content: bytes = CONTENT
) -> Tuple[str, bytes]:
    body = (
        f"--{BOUNDARY}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        "Content-Type: text/plain\r\n"
        "\r\n"
    ).encode()
    body += content
    body += f"\r\n--{BOUNDARY}--\r\n".encode()
    return f"multipart/form-data; boundary={BOUNDARY}", body


def assert_secure_upload_response(resp_dict: dict) -> None:
    assert resp_dict["filename"] == FILENAME
    assert resp_dict["size"] == len(CONTENT)
    assert resp_dict["chunks_processed"] > 0
    assert resp_dict["sha256"] == hashlib.sha256(CONTENT).hexdigest()
    assert resp_dict["status"] == "uploaded successfully"


def assert_upload_progress_response(resp_dict: dict) -> None:
    assert resp_dict["filename"] == FILENAME
    assert resp_dict["total_size"] == len(CONTENT)
    assert resp_dict["chunks_processed"] > 0
    assert resp_dict["progress"] == 100.0
    assert resp_dict["status"] == "completed"
