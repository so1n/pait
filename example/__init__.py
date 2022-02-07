import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


@pait()
async def demo(
    demo_value1: dict = field.Body.i(raw_return=True),
    a: str = field.Body.i(),
) -> JSONResponse:
    return JSONResponse({"demo_value": demo_value1, "a": a})


app = Starlette(routes=[Route("/api/demo", demo, methods=["POST"])])

uvicorn.run(app)
