from sanic import HTTPResponse, Request, Sanic, json

from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return json({"data": str(exc)})


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
async def demo(token: str = field.Depends.i(GetUserDepend)) -> HTTPResponse:
    return json({"user": token})


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
