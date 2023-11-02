from sanic import Sanic
from sanic.request import Request

from pait.app.any import SimpleRoute, add_multi_simple_route, add_simple_route
from pait.app.sanic import pait
from pait.model import response


@pait(response_model_list=[response.JsonResponseModel])
async def json_route(request: Request) -> dict:
    return {}


@pait(response_model_list=[response.TextResponseModel])
async def text_route(request: Request) -> str:
    return "demo"


@pait(response_model_list=[response.HtmlResponseModel])
async def html_route(request: Request) -> str:
    return "<h1>demo</h1>"


app: Sanic = Sanic("demo")
add_simple_route(app, SimpleRoute(route=json_route, url="/json", methods=["GET"]))
add_multi_simple_route(
    app,
    SimpleRoute(route=json_route, url="/json", methods=["GET"]),
    SimpleRoute(route=text_route, url="/text", methods=["GET"]),
    SimpleRoute(route=html_route, url="/html", methods=["GET"]),
    prefix="/api",
    title="api",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
