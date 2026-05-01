import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from pait.app.starlette import APIRoute

api_route = APIRoute(path="/api")


@api_route.get("/health", framework_extra_param={"name": "extra_health"})
async def health() -> JSONResponse:
    return JSONResponse({"ok": True})


def create_app() -> Starlette:
    app = Starlette()
    api_route.inject(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
