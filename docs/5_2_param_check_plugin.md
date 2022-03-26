`Pait`基于`Pydantic`实现了很多参数校验和转换的功能，但是在开发API的过程中，往往还需要一些参数依赖相关的校验功能，
在`Pait`中通过后置插件`Required`和`AtMostOneOf`提供两种参数依赖校验功能。

## Required插件
在编写API接口时，经常会遇到一种情况，比如某个接口存在请求参数A，B，C，一般情况下B和C都是选填，但是参数C依赖于参数B，也就是参数B存在时，C才可以存在，
这时就可以使用`Required`插件配置规则来满足这一个条件，如下代码：
```py hl_lines="23-25"
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException
from pait.plugin import PluginManager
from pait.plugin.required import AsyncRequiredPlugin

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait(
    post_plugin_list=[
        PluginManager(AsyncRequiredPlugin, required_dict={"email": ["user_name"]})
    ]
)
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None)
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
这个函数本意上要求的是参数`uid`为必填参数，而参数`user_name`和`email`是选填参数，但是通过使用`AsyncReuiredPlugin`插件后就会新增一个校验逻辑，
这个校验逻辑是由参数`required_dict`定义的，它表示的是参数`email`必须依赖于一个参数集合才可以存在，这里定义的集合只有一个参数--`user_name`

使用`curl`发送请求后可以通过响应结果发现，如果请求的参数只有`uid`时能正常返回，但请求的参数`user_name`为空时，参数`email`必须为空，不然会报错。
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"data":"email requires param user_name, which if not none"}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":"aaa"}%
```

!!! note
    对于同步函数，请选用`ReuiredPlugin`插件

## AtMostOneOf插件
除了参数的互相依赖外，还存在参数互相排斥的情况，比如某个接口有参数A，B，C三个，当B存在时，C就不能存在，C存在时，B就不能存在，这时可以使用`AtMostOneOf`插件配置规则来实现功能，代码如下：
```py hl_lines="23-28"
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException
from pait.plugin import PluginManager
from pait.plugin.at_most_one_of import AsyncAtMostOneOfPlugin

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait(
    post_plugin_list=[
        PluginManager(
            AsyncAtMostOneOfPlugin,
            at_most_one_of_list=[["email", "user_name"]]
        )
    ]
)
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None)
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```

这个函数本意上要求的是参数`uid`为必填参数，而参数`user_name`和`email`是选填参数，但是通过`AsyncAtMostOneOfPlugin`插件后就会新增一个校验逻辑，
这个校验逻辑是由参数`at_most_one_of_list`定义的，它表示的是某一组参数不能同时存在，这里定义的是参数`email`和`user_name`不能同时存在。

使用`curl`发送请求后可以通过响应结果发现，参数`email`和`user_name`共存时候会返回错误，其它情况都能正常返回响应。
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"uid":"123","user_name":null,"email":"aaa"}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"data":"requires at most one of param email or user_name"}%
```

!!! note
    对于同步函数，请选用`AtMostOneOfPlugin`插件
