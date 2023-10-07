from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


class GetUserDepend(object):
    user_name: str = field.Query.i()

    async def __call__(self, token: str = field.Header.i()) -> str:
        if token not in fake_db_dict:
            raise RuntimeError(f"Can not found by token:{token}")
        user_name = fake_db_dict[token]
        if user_name != self.user_name:
            raise RuntimeError("The specified user could not be found through the token")
        return user_name


@pait()
async def demo(token: str = field.Depends.i(GetUserDepend)) -> JSONResponse:
    return JSONResponse({"user": token})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
