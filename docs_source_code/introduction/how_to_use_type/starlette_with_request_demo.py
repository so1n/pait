from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait


@pait()
async def demo(req: Request) -> JSONResponse:
    return JSONResponse({"url": str(req.url.path), "method": req.method})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
