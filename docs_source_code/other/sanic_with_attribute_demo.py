import httpx
from sanic import HTTPResponse, Request, Sanic, json

from pait.app.any import get_app_attribute, set_app_attribute


async def demo_route(request: Request) -> HTTPResponse:
    client: httpx.AsyncClient = get_app_attribute(request.app, "client")
    return json({"status_code": (await client.get("http://so1n.me")).status_code})


app: Sanic = Sanic("demo")
app.add_route(demo_route, "/api/demo", methods=["GET"])
set_app_attribute(app, "client", httpx.AsyncClient())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
