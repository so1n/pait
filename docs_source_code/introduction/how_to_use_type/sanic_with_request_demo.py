from sanic import Request, Sanic, json, response

from pait.app.sanic import pait


@pait()
async def demo(req: Request) -> response.HTTPResponse:
    return json({"url": req.path, "method": req.method})


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
