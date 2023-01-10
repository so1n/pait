import time
from tempfile import NamedTemporaryFile
from typing import Any, AsyncContextManager, Optional

import aiofiles  # type: ignore
from starlette.background import BackgroundTask
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

from example.common import response_model, tag
from example.starlette_example.utils import api_exception, global_pait
from pait.app.starlette import Pait
from pait.field import Query
from pait.model.status import PaitStatus

check_resp_pait: Pait = global_pait.create_sub_pait(
    group="check_resp", tag=(tag.check_resp_tag,), status=PaitStatus.release
)


@check_resp_pait(response_model_list=[response_model.TextRespModel])
async def async_text_response_route() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[response_model.TextRespModel])
def text_response_route() -> PlainTextResponse:
    response: PlainTextResponse = PlainTextResponse(str(time.time()))
    response.media_type = "text/plain"
    response.headers.append("X-Example-Type", "text")
    return response


@check_resp_pait(response_model_list=[response_model.HtmlRespModel])
async def async_html_response_route() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[response_model.HtmlRespModel])
def html_response_route() -> HTMLResponse:
    response: HTMLResponse = HTMLResponse("<H1>" + str(time.time()) + "</H1>")
    response.media_type = "text/html"
    response.headers.append("X-Example-Type", "html")
    return response


@check_resp_pait(response_model_list=[response_model.FileRespModel])
def file_response_route() -> FileResponse:
    named_temporary_file = NamedTemporaryFile(delete=True)
    f: Any = named_temporary_file.__enter__()
    f.write("Hello Word!".encode())
    f.seek(0)

    def close_file() -> None:
        named_temporary_file.__exit__(None, None, None)

    response: FileResponse = FileResponse(
        f.name, media_type="application/octet-stream", background=BackgroundTask(close_file)
    )
    response.headers.append("X-Example-Type", "file")
    return response


@check_resp_pait(response_model_list=[response_model.FileRespModel])
async def async_file_response_route() -> FileResponse:
    named_temporary_file: AsyncContextManager = aiofiles.tempfile.NamedTemporaryFile()  # type: ignore
    f: Any = await named_temporary_file.__aenter__()
    await f.write("Hello Word!".encode())
    await f.seek(0)

    async def close_file() -> None:
        await named_temporary_file.__aexit__(None, None, None)

    response: FileResponse = FileResponse(
        f.name, media_type="application/octet-stream", background=BackgroundTask(close_file)
    )
    response.headers.append("X-Example-Type", "file")
    return response


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
) -> JSONResponse:
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
    return JSONResponse(return_dict)


if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route

    from pait.app.starlette import add_doc_route
    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])

    app: Starlette = Starlette(
        routes=[
            Route("/api/check-resp", check_response_route, methods=["GET"]),
            Route("/api/text-resp", text_response_route, methods=["GET"]),
            Route("/api/html-resp", html_response_route, methods=["GET"]),
            Route("/api/file-resp", file_response_route, methods=["GET"]),
            Route("/api/async-text-resp", async_text_response_route, methods=["GET"]),
            Route("/api/async-html-resp", async_html_response_route, methods=["GET"]),
            Route("/api/async-file-resp", async_file_response_route, methods=["GET"]),
        ]
    )
    app.add_exception_handler(Exception, api_exception)
    add_doc_route(prefix="/api-doc", title="Grpc Api Doc", app=app)
    uvicorn.run(app)
