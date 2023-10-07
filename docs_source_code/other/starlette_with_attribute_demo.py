import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse

from pait.app import get_app_attribute, set_app_attribute


async def demo_route(request: Request) -> JSONResponse:
    client: httpx.AsyncClient = get_app_attribute(request.app, "client")
    return JSONResponse({"status_code": (await client.get("http://so1n.me")).status_code})


app: Starlette = Starlette()
app.add_route("/api/demo", demo_route, methods=["GET"])
set_app_attribute(app, "client", httpx.AsyncClient())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
