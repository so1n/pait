`Pait`内部有很多参数校验逻辑，出现错误的情况也有很多种，为了方便的捕获和了解异常，`Pait`拥有一个简单的异常机制。
`Pait`的异常都是继承于`PaitBaseException`，在发生异常时可以通过:
```python
isinstance(exc, PaitBaseException)
```
来判断异常是否属于`Pait`的异常。

!!! note
    由于`Pait`是使用`Pydantic`进行校验， 所以在运行时会因为校验不通过而抛出`Pydantic`相关异常，
    可以通过[Error Handling](https://pydantic-docs.helpmanual.io/usage/models/#error-handling)了解如何使用`Pydantic`异常
## TipException异常
`Pait`的核心是一个装饰器，在运行的时候`Pait`核心会检查参数是否存在，参数是否合法，以及参数是否通过`Pydantic`的校验，
在上述条件中有一个校验不通过时都会抛出异常，但是该异常的堆栈只会在`Pait`的核心装饰器里流转，这样子对于使用`Pait`的开发者来说很难找出出现问题的路由函数在哪，这样排查问题是十分困难的。
所以`Pait`通过`TipException`对异常进行一个包装，在抛错信息里告诉用户说哪个路由函数抛错，抛错的位置在哪里，
如果用户使用了类似于`Pycharm`的IDE,还可以通过点击路径跳转到对应的地方，一个异常示例如下：
```bash
Traceback (most recent call last):
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/exceptions.py", line 71, in __call__
    await self.app(scope, receive, sender)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 583, in __call__
    await route.handle(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 243, in handle
    await self.app(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 54, in app
    response = await func(request)
  File "/home/so1n/github/pait/pait/core.py", line 232, in dispatch
    return await first_plugin(*args, **kwargs)
  File "/home/so1n/github/pait/pait/param_handle.py", line 448, in __call__
    async with self:
  File "/home/so1n/github/pait/pait/param_handle.py", line 456, in __aenter__
    raise e from gen_tip_exc(self.call_next, e)
  File "/home/so1n/github/pait/pait/param_handle.py", line 453, in __aenter__
    await self._gen_param()
  File "/home/so1n/github/pait/pait/param_handle.py", line 439, in _gen_param
    self.args, self.kwargs = await self.param_handle(func_sig, func_sig.param_list)
  File "/home/so1n/github/pait/pait/param_handle.py", line 396, in param_handle
    await asyncio.gather(*[_param_handle(parameter) for parameter in param_list])
  File "/home/so1n/github/pait/pait/param_handle.py", line 393, in _param_handle
    raise gen_tip_exc(_object, closer_e, parameter)
pait.exceptions.TipException: Can not found content__type value for <function raise_tip_route at 0x7f512ccdebf8>   Customer Traceback:
    File "/home/so1n/github/pait/example/param_verify/starlette_example.py", line 88, in raise_tip_route.
```
可以看到异常是通过`gen_tip_exc`抛出来的，而抛出来的异常信息则包含路由函数所在位置，和异常信息，此外，可以通过`TipException.exc`获取到原本的异常。

## 参数异常
目前`Pait`有3种参数异常，分别有:

- NotFoundFieldException  该异常表示匹配不到对应的`Field`， 通常开发者在正常使用时，不会遇到该异常。
- NotFoundValueException  该异常表示无法从请求数据中找到对应的值，这是一个常见的异常，一般是请求数据缺少部分参数。
- FieldValueTypeException  该异常表示程序启动时，`Pait`发现`Field`里的`default`，`example`等填写的值不合法，开发者需要根据提示进行改正。

这三种异常都是继承于`PaitBaseParamException`，它的源码如下：
```Python
class PaitBaseParamException(PaitBaseException):
    def __init__(self, param: str, msg: str):
        super().__init__(msg)
        self.param: str = param
        self.msg: str = msg
```
从代码可以看出`PaitBaseParamException`在抛异常时只会抛出错误信息，但是在需要根据异常返回一些指定响应时，可以通过`param`知道是哪个参数出错。

## 异常使用示例
在CRUD业务中，路由函数发生的异常都要被捕获，然后返回一个协定好的错误信息供前端使用，下面是一个异常捕获的示例代码：
```py hl_lines="13"
from typing import List
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field, exceptions
from pait.app.starlette import pait
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, exceptions.TipException):
        # 提取原本的异常
        exc = exc.exc

    if isinstance(exc, exceptions.PaitBaseParamException):
        # 提取参数信息和错误信息，告知用户哪个参数发生错误
        return JSONResponse({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, ValidationError):
        # 解析Pydantic异常，返回校验失败的参数信息
        error_param_list: List[str] = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return JSONResponse({"code": -1, "msg": f"check error param: {error_param_list}"})
    elif isinstance(exc, exceptions.PaitBaseException):
        # 标准的Pait异常，通常很少出现，直接返回异常信息
        return JSONResponse({"code": -1, "msg": str(exc)})

    # 路由函数的错误信息
    return JSONResponse({"code": -1, "msg": str(exc)})


@pait()
async def demo(demo_value: int = field.Query.i()) -> JSONResponse:
    return JSONResponse({"code": 0, "msg": "", "data": demo_value})

app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```
该代码的响应使用了常见的后端返回Json数据协议:
```json
{
  "code": 0,
  "msg": "",
  "data": {}
}
```
其中`code`为0时代表响应正常，不为0则为异常且`msg`包括了一个错误信息供前端展示，而`data`是正常响应时的结构体。

然后通过`Starlette`框架的异常机制，把自定义的`api_exception`函数挂载到`Starlette`的异常处理回调中，
`api_exception`函数里面包含了使用`Pait`时遇到的几种异常的处理，然后按照协议返回数据给调用端，通过`curl`调用可以发现：

- 缺少参数时，会返回找不到参数的错误信息
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo"
    {"code":-1,"msg":"error param:demo_value, Can not found demo_value value"}
    ```
- 参数校验出错时，会返回校验出错的参数名
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=a"
    {"code":-1,"msg":"check error param: ['demo_value']"}
    ```
- 参数正常时返回正常的数据
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=3"
    {"code":0,"msg":"","data":3}
    ```
