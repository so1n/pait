`Pait`自带是插件并不多，但开发者可以根据自己的需求实现插件，下面以异常捕获插件为例子阐述如何制作一个插件。

下面所示代码是一个简单的API接口：
```py
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait()
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
这个接口由`Pait`提供参数校验功能，如果调用方发起的参数有错，则会直接抛出异常并最终被`starlette`捕获再分发到`api_exception`函数处理，比如下面的请求，
`Pait`在校验发现缺少参数uid时会抛出错误，最后被`api_exception`捕获并把异常返回给调用方：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"data":"Can not found uid value"}
```
现在该接口多了一个需求，需要对该路由函数的异常的处理定制化，生成不一样的返回格式，但是`api_exception`是统一处理所有接口函数的异常，
它不可能为每个函数定义一个单独的函数处理，这时候可以定制一个捕获异常的插件来解决这个问题，如下是一个单独针对这个接口定制的插件：
```py linenums="1"
from typing import Any, Dict
from pait.plugin.base import BaseAsyncPlugin
from pait.model.core import PaitCoreModel
from pydantic import ValidationError
from pait.exceptions import PaitBaseException


class DemoExceptionPlugin(BaseAsyncPlugin):
    is_pre_core: bool = True

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if pait_core_model.func.__name__ != "demo":
            raise RuntimeError(f"The {cls.__name__} is only used for demo func")
        return super().pre_load_hook(pait_core_model, kwargs)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return await self.call_next(args, kwargs)
        except (ValidationError, PaitBaseException) as e:
            return JSONResponse({"plugin exc info": str(e)})
```
在这个示例插件中，需要注意的有几个地方：

- 0.由于该路由函数是`async`的，所以该函数只能被基于`BaseAsyncPlugin`插件挂载。
- 1.第9行的`is_pre_core = True`是设置该插件为前置插件，这样就能拦截`Pait`和路由函数的异常了。
- 2.第12行的`pre_load_hook`方法会进行一些初始化的检查，该检查只会在初始化的时候运行，这个检查的逻辑是如果判定该插件并不是挂在`demo`函数上就会抛错，
其中`pait_core_model`是`Pait`为路由函数生成的一些属性。
- 3.第17行的`__call__`方法是该插件的主要处理逻辑，当有请求进来时，`Pait`会通过`__call__`方法调用插件，插件可以通过`call_next`来调用下一个插件，
该插件通过`try...except`来捕获后续所有调用段异常，如果是符合条件的异常就会被捕获，并生成不一样的响应结果。

编写完毕插件后，通过`PluginManager`托管挂载插件:
```python
from pait.plugin import PluginManager


@pait(plugin_list=[PluginManager(DemoExceptionPlugin)])
async def demo(...): pass
```
最后重启程序并运行同样的请求，可以发现响应结果已经变为插件自己抛出的结果：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"plugin exc info":"File \"/home/so1n/demo.py\", line 48, in demo.\nerror:Can not found uid value"}
```
