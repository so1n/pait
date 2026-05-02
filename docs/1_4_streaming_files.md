# Streaming File Upload

File upload is a common requirement in web applications. Traditional upload handling usually loads the entire file into
memory, which can consume a large amount of memory when the uploaded file is large.
`Pait` provides streaming file upload support through the `StreamFile` field. It is suitable for large file processing
and for scenarios that need upload progress tracking.

!!! warning
    Tornado does not currently support `StreamFile` streaming upload in Pait. The examples on this page apply to
    Flask, Starlette, and Sanic only.

## 1.Advantages of streaming upload

Traditional file upload uses the `File` field and reads the whole file into memory at once. Streaming upload processes
the file in chunks and has the following advantages:

- **Efficient memory usage**: Only a small buffer is needed to process files of any size
- **Large file support**: GB-level files can be processed without loading them completely into memory
- **Real-time processing**: File data can be processed while it is being received, such as hashing or scanning
- **Progress tracking**: Upload progress can be tracked while the stream is being consumed

`Pait` provides two streaming implementations:

- **Multipart Streaming**: Based on the `multipart` library, with better compatibility and richer metadata access
- **Streaming Form Data**: Based on the `streaming-form-data` library, with better performance and lower memory usage

## 2.Install dependencies

Streaming file upload requires extra dependencies:

```bash
# Install multipart support
pip install pait[multipart]

# Install streaming-form-data support. This is recommended for better performance.
pip install pait[streaming_form_data]

# Install both streaming implementations
pip install "pait[multipart,streaming_form_data]"
```

!!! note
    `streaming-form-data` is recommended for large file uploads because it has better performance and lower memory
    usage. `pait[all]` does not include these two streaming upload dependencies.

## 3.Multipart Streaming

Multipart Streaming uses the `multipart` library for parsing and provides richer file metadata access. The following
examples show how to use it in supported web frameworks:

=== "Flask"

    ```py linenums="1" title="docs_source_code/streaming_files/flask_multipart_demo.py"
    --8<-- "docs_source_code/streaming_files/flask_multipart_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/streaming_files/starlette_multipart_demo.py"
    --8<-- "docs_source_code/streaming_files/starlette_multipart_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/streaming_files/sanic_multipart_demo.py"
    --8<-- "docs_source_code/streaming_files/sanic_multipart_demo.py"
    ```

The usage is mostly the same across frameworks. The main differences are:

- **Sync frameworks** such as Flask use the `Stream` class and a normal `for` loop
- **Async frameworks** such as Starlette and Sanic use the `AsyncStream` class and an `async for` loop
- **Sanic** requires `stream=True` in the route definition

Use `stream.stream()` to get an iterator over file chunks, `stream.filename()` to get the filename, and `stream.info()`
to get file metadata such as `Content-Type`.

## 4.Streaming Form Data

Streaming Form Data uses the `streaming-form-data` library and performs better when processing large files:

=== "Flask"

    ```py linenums="1" title="docs_source_code/streaming_files/flask_sfd_demo.py"
    --8<-- "docs_source_code/streaming_files/flask_sfd_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/streaming_files/starlette_sfd_demo.py"
    --8<-- "docs_source_code/streaming_files/starlette_sfd_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/streaming_files/sanic_sfd_demo.py"
    --8<-- "docs_source_code/streaming_files/sanic_sfd_demo.py"
    ```

Compared with Multipart Streaming, Streaming Form Data is simpler and faster, so it is the recommended implementation
for large file uploads.

## 5.Stream methods and properties

Both `MultipartStream` and `SFDStream` provide similar methods for accessing file data and metadata:

### 5.1.Core methods

- **`stream()`**: Returns an iterator or async iterator of file chunks. Each chunk is `bytes`
- **`filename()`**: Returns the filename extracted from the multipart form data
- **`info()`**: Only available on `MultipartStream`; returns detailed file metadata

### 5.2.Usage example

```python
# Get filename
filename = stream.filename()  # sync version
filename = await stream.filename()  # async version

# Get file metadata. Only available with Multipart Streaming.
info = stream.info()  # sync version
info = await stream.info()  # async version

if info:
    content_type = info.content_type
    content_disposition = info.content_disposition
```

## 6.Advanced examples

### 6.1.Secure file upload and validation

In real applications, uploaded files usually need validation and secure handling. The following example validates the
filename, calculates the SHA256 hash while streaming, and saves the file safely:

=== "Flask"

    ```py linenums="1" title="docs_source_code/streaming_files/flask_secure_upload_demo.py"
    --8<-- "docs_source_code/streaming_files/flask_secure_upload_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/streaming_files/starlette_secure_upload_demo.py"
    --8<-- "docs_source_code/streaming_files/starlette_secure_upload_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/streaming_files/sanic_secure_upload_demo.py"
    --8<-- "docs_source_code/streaming_files/sanic_secure_upload_demo.py"
    ```

This example demonstrates how to:

- Validate filenames and prevent path traversal
- Calculate the SHA256 hash while streaming the file
- Count processed chunks
- Save the uploaded file to a controlled directory

Use the following `curl` command to test the route:

```bash
printf "hello pait" > /tmp/pait-upload-demo.txt
curl -X POST \
  -F "stream=@/tmp/pait-upload-demo.txt" \
  http://127.0.0.1:8000/api/secure-upload
```

### 6.2.Upload progress tracking

Streaming makes it straightforward to track upload progress while processing the file:

=== "Flask"

    ```py linenums="1" title="docs_source_code/streaming_files/flask_upload_progress_demo.py"
    --8<-- "docs_source_code/streaming_files/flask_upload_progress_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/streaming_files/starlette_upload_progress_demo.py"
    --8<-- "docs_source_code/streaming_files/starlette_upload_progress_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/streaming_files/sanic_upload_progress_demo.py"
    --8<-- "docs_source_code/streaming_files/sanic_upload_progress_demo.py"
    ```

The example uses the `X-File-Size` header as the expected file size and calculates progress from the number of processed
bytes. Use the following `curl` command to test the route:

```bash
printf "hello pait" > /tmp/pait-upload-demo.txt
curl -X POST \
  -H "X-File-Size: 10" \
  -F "stream=@/tmp/pait-upload-demo.txt" \
  http://127.0.0.1:8000/api/upload-progress
```
