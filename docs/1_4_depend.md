`Pait`的`Depend`参考了[FastAPI](https://github.com/tiangolo/fastapi)，它的作用跟[FastAPI](https://github.com/tiangolo/fastapi)很像，
用户通过`Pait`的`Depend`可以一些功能:

- 共享一些相同的逻辑
- 实现一些安全校验的功能
- 与别的系统交互(如数据库)。

> NOTE：示例代码都是使用`async def`语法，实际上也是支持`def`语法。

## 1.使用Depend功能
一般的后端系统中都带有用户Token校验业务，这个业务是非常符合Depend的使用场景。
在这个场景中，用户每次访问接口时都需要带上Token，服务端收到用户的请求后会先判断Token是否合法，如果不合法则会返回错误，合法则会执行接口的逻辑。

如果在使用类`Flask`这类型的微Web框架，那么都会选择使用Python装饰器的方法来实现共享用户Token校验，有些时候除了实现校验Token外，
还会根据Token获取uid并传给路由函数的功能，但是这种实现方法比较动态，代码检测工具很难检测出来，而使用`Pait`的`Depend`可以解决这个问题。

示例代码如下，其中第一段高亮是模仿数据库的调用方法，目前假设数据库只有token为"u12345"的值；第二段高亮是一个特殊的函数，这段函数可以被`Pait`的`Depend`使用，
所以这个函数的参数填写规则与`Pait`装饰的路由函数一致，之前提到的任何写法都可以在这个函数中使用，而目前这个函数的功能就是从Header中获取Token，并校验Token是否存在，
如果存在则返回用户，不存在则抛错。
```py hl_lines="16 19-22 26"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


async def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait()
async def demo(token: str = field.Depends.i(get_user_by_token)) -> JSONResponse:
    return JSONResponse({"user": token})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```
接着使用`curl`命令进行测试，发现这段代码工作一切正常，token存在则返回用户，不存在则返回抛错信息:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```

此外，`Pait`能支持多层Depend嵌套的，但是一般不推荐嵌套的层数太多，以上面的代码为例子，假设Token要经过一层特别的校验，且该校验逻辑会被复用，则代码可以改写为：
```py hl_lines="19-22 25"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


def check_token(token: str = field.Header.i()) -> str:
    if len(token) != 6 and token[0] != "u":
        raise RuntimeError("Illegal Token")
    return token


async def get_user_by_token(token: str = field.Depends.i(check_token)) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait()
async def demo(token: str = field.Depends.i(get_user_by_token)) -> JSONResponse:
    return JSONResponse({"user": token})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```
其中高亮部分为新修改的地方， 主要是新增了一个`check_token`的函数，用来获取和校验Token，而`get_user_by_token`则依赖于`check_token`获取Token并判断用户是否存在。
使用`curl`进行接口测试，发现响应结果正常，不符合校验逻辑的会返回抛错信息：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:fu12345"
{"data":"Illegal Token"}
```

## 2.结合Python ContextManager的Depend
上述所示的`Depends`用法虽然能正常的使用，但是它不能像Python装饰器一样知道函数的运行情况，包括函数是否正常运行，函数何时运行结束等，
针对这个问题`Pait`采用了和`pytest.fixture`一样的解决方案--引入`ContextManager`。

这种方式的使用方法很简单，只要把函数加上对应的`ContextManager`装饰器，然后按照官方文档使用`try`,`except`,`finally`语法块即可实现，如下例子:
```Python
from contextlib import contextmanager
from typing import Any, Generator

@contextmanager
def demo() -> Generator[Any, Any, Any]:
    try:
        # 1
        yield None
    except Exception:
        # 2
        pass
    finally:
        # 3
        pass
```
该例子中序号1的位置用来编写正常的函数逻辑，并通过yield返回数据，序号2的位置用来写当函数运行异常时的代码逻辑，最后的序号3则是一个统一的函数运行结束处理逻辑。

!!! note

    `ContextManager`的`Depend`函数除了参数外，其余的编写方法和官方的一致，具体可见[contextlib — Utilities for with-statement contexts](https://docs.python.org/3/library/contextlib.html)

下面的代码是一个使用了`ContextManager`的`Depend`例子， 该例子假设每次调用请求时都会基于对应的uid创建一个Session，请求结束时会自动关闭：
```py hl_lines="19-35 38-49 52-58"
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


class _DemoSession(object):
    def __init__(self, uid: int) -> None:
        self._uid: int = uid
        self._status: bool = False

    @property
    def uid(self) -> int:
        if self._status:
            return self._uid
        else:
            raise RuntimeError("Session is close")

    def create(self) -> None:
        self._status = True

    def close(self) -> None:
        self._status = False


@asynccontextmanager
async def async_context_depend(uid: int = field.Query.i(description="user id", gt=10, lt=1000)) -> AsyncGenerator[int, Any]:
    session: _DemoSession = _DemoSession(uid)
    try:
        print("context_depend init")
        session.create()
        yield session.uid
    except Exception:
        print("context_depend error")
    finally:
        print("context_depend exit")
        session.close()


@pait()
async def demo(
    uid: str = field.Depends.i(async_context_depend), is_raise: bool = field.Query.i(default=False)
) -> JSONResponse:
    if is_raise:
        raise RuntimeError()
    return JSONResponse({"code": 0, "msg": uid})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```
代码中第一段高亮是模拟一个基于Uid的Session，第二段高亮则是一段带有`ContextManger`的Depends函数，并分别在`try`, `except`以及`finally`打印不同的内容，
而第三块则是路由函数，它会依据参数`is_raise`是否为`True`来决定抛错还是正常返回。

现在运行代码并使用`curl`进行接口测试，发现第一个请求是通过的，但是第二个请求发生异常：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=999"
{"code":0,"msg":999}
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=999&is_raise=True"
{"data":""}
```
这时切回到运行Python进程的终端，可以发现终端打印了如下数据:
```bash
context_depend init
context_depend exit
INFO:     127.0.0.1:44162 - "GET /api/demo?uid=999 HTTP/1.1" 200 OK
context_depend init
context_depend error
context_depend exit
INFO:     127.0.0.1:44164 - "GET /api/demo?uid=999&is_raise=True HTTP/1.1" 200 OK
```
从输出的数据可以看出， 对于第一个请求只打印了`init`和`exit`，而对于第二个会产生异常的请求则多打印了`error`。
## 3.Pre-Depend
在一些场景下只需要`Depends`函数执行校验逻辑，如果校验失败就抛出错误，接口并不需要`Depends`函数的返回值，比如在第一个场景中，
不需要用到函数`get_user_by_token`的返回值，代码则会变成这样:
```py hl_lines="26"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


async def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait()
async def demo(token: str = field.Depends.i(get_user_by_token)) -> JSONResponse:
    return JSONResponse({"msg": "success"})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```
如果这段代码是使用IDE进行编写的，那么高亮处的token变量会被打上下划线，如果使用`pyflake`进行代码检测，可能会检查不通过，这时可以把高亮处代码的token参数名改为`_`:
```python

@pait()
async def demo(_: str = field.Depends.i(get_user_by_token)) -> JSONResponse:
    return JSONResponse({"msg": "success"})
```
来解决问题， 但是Python是不支持一个函数内出现相同名字的变量， 这意味着有多个类似的参数时，不能把他们变量名都改为`_`。

为此，`Pait`通过可选参数`pre_depend_list`来提供了`Pre-Depends`功能，用户只需要把函数传入到Pait的pre_depend_list可选参数即可，
代码的逻辑和功能均不会被受到影响，这样修改后代码会变为如下：
```py hl_lines="25 26"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


async def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait(pre_depend_list=[get_user_by_token])
async def demo() -> JSONResponse:
    return JSONResponse({"msg": "success"})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)
```

!!! note
    这种情况下`Pait`会先执行`pre_depend_list`的函数再执行路由函数。
