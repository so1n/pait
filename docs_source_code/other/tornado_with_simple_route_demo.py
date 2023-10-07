from tornado.ioloop import IOLoop
from tornado.web import Application

from pait.app import SimpleRoute, add_multi_simple_route, add_simple_route
from pait.app.tornado import pait
from pait.model import response


@pait(response_model_list=[response.JsonResponseModel])
async def json_route() -> dict:
    return {}


@pait(response_model_list=[response.TextResponseModel])
async def text_route() -> str:
    return "demo"


@pait(response_model_list=[response.HtmlResponseModel])
async def html_route() -> str:
    return "<h1>demo</h1>"


app: Application = Application()
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
    app.listen(8000)
    IOLoop.instance().start()
