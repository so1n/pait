import time
from typing import Any, AsyncContextManager, Optional

import aiofiles  # type: ignore
from sanic import Request, response

from example.common import response_model, tag
from example.sanic_example.utils import create_app, global_pait
from pait.app.sanic import Pait
from pait.field import Query
from pait.model.status import PaitStatus

check_resp_pait: Pait = global_pait.create_sub_pait(
    group="check_resp", tag=(tag.check_resp_tag,), status=PaitStatus.release
)


@check_resp_pait(response_model_list=[response_model.TextRespModel])
async def text_response_route(request: Request) -> response.HTTPResponse:
    return response.text(str(time.time()), headers={"X-Example-Type": "text"})


@check_resp_pait(response_model_list=[response_model.HtmlRespModel])
async def html_response_route(request: Request) -> response.HTTPResponse:
    return response.text(
        "<H1>" + str(time.time()) + "</H1>", headers={"X-Example-Type": "html"}, content_type="text/html"
    )


@check_resp_pait(response_model_list=[response_model.FileRespModel])
async def file_response_route(request: Request) -> response.StreamingHTTPResponse:
    # sanic file response will return read file when `return resp`
    named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
    f: Any = await named_temporary_file.__aenter__()
    await f.write("Hello Word!".encode())
    await f.seek(0)
    resp: response.StreamingHTTPResponse = await response.file_stream(f.name, mime_type="application/octet-stream")
    resp.headers.add("X-Example-Type", "file")

    raw_streaming_fn = resp.streaming_fn

    async def _streaming_fn(_response: response.BaseHTTPResponse) -> None:
        await raw_streaming_fn(_response)
        await named_temporary_file.__aexit__(None, None, None)

    resp.streaming_fn = _streaming_fn
    return resp


@check_resp_pait(
    append_tag=(tag.user_tag,),
    response_model_list=[response_model.UserSuccessRespModel3, response_model.FailRespModel],
)
async def check_response_route(
    uid: int = Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = Query.i(default="example@xxx.com", description="user email"),
    user_name: str = Query.i(description="user name", min_length=2, max_length=4),
    age: int = Query.i(description="age", gt=1, lt=100),
    display_age: int = Query.i(0, description="display_age"),
) -> response.HTTPResponse:
    """Test test-helper check response"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return response.json(return_dict)


if __name__ == "__main__":
    with create_app(__name__) as app:
        app.add_route(check_response_route, "/api/check-resp", methods={"GET"})
        app.add_route(text_response_route, "/api/text-resp", methods={"GET"})
        app.add_route(html_response_route, "/api/html-resp", methods={"GET"})
        app.add_route(file_response_route, "/api/file-resp", methods={"GET"})
