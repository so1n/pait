from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def demo_post(request: Request) -> JSONResponse:
    request_dict = await request.json()
    uid_str: str = request_dict.get("uid", "")
    username: str = request_dict.get("username", "")

    uid = int(uid_str)  # 暂时不去考虑类型转换的异常
    if not (10 < uid < 1000):
        raise ValueError("invalid uid")
    if not (2 <= len(username) <= 4):
        raise ValueError("invalid name")
    # 获取对应的值进行返回
    return JSONResponse({"uid": uid, "username": username})


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
