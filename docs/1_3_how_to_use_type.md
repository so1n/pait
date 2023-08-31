`Type`用于指明该参数值的最终类型是什么，在上面的示例中，`Pait`在内部会把用户填写的值转换为`Pydantic.BaseModel`，并通过`pydantic`进行校验，
如下面的接口:
```Python hl_lines="3-4"
@pait()
async def demo(
    a: str = field.Body.i(),
    b: int = field.Body.i(),
) -> JSONResponse:
    return JSONResponse({"a": a, "b": b})
```
在`Pait`内部， 会认为该接口需要的是一个如下的`Pydantic.BaseModel`:
```Python
from pydantic import BaseModel, Field

class Demo(BaseModel):
    a: str = Field()
    b: int = Field()
```
所以在接口中`Type`可以变得非常灵活，你可以像[Pydantic Field Types](https://pydantic-docs.helpmanual.io/usage/types/)一样使用以及直接使用[Pydantic Field Types](https://pydantic-docs.helpmanual.io/usage/types/)的拓展Type。
此外，`Pait`的`Type`还支持其它的功能。
## 1.使用Pydantic.BaseModel
在使用了`Pait`一段时间后，会发现有些接口的参数可能可以复用，这时可以采用`Type`为Pydantic.BaseModel的方案，把两个接口重复的参数抽象为一个pydantic.Basemodel

示例代码如下， 首先是12行的`DemoModel`，它继承于`Pydantic.BaseModel`且有三个属性分别为`uid`,`name`以及`age`，然后有两个不一样的接口，
接口`demo`从Url中获取所有的值，并交给`DemoModel`进行校验，然后通过`.dict`方法生成dict并返回。接口`demo1`与接口`demo`很像， 只不过是从Json Body获取数据。
```py linenums="1" hl_lines="12-15 19 24"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait

from pydantic import BaseModel


class demomodel(basemodel):
    uid: str
    name: str
    age: int


@pait()
async def demo(demo_model: DemoModel = field.Query.i(raw_return=True)) -> JSONResponse:
    return JSONResponse(demo_model.dict())


@pait()
async def demo1(demo_model: DemoModel = field.Body.i(raw_return=True)) -> JSONResponse:
    return JSONResponse(demo_model.dict())


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"]), Route("/api/demo1", demo1, methods=["POST"])])

uvicorn.run(app)
```
接下来使用`curl`对两个接口进行测试：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=u12345&name=so1n&age=10"
{"uid":"u12345","name":"so1n","age":10}
➜  ~ curl "http://127.0.0.1:8000/api/demo1" -X POST -d '{"uid": "u12345", "name": "so1n", "age": 10}' --header "Content-Type: application/json"
{"uid":"u12345","name":"so1n","age":10}
```
可以发现两个接口都能正常的工作，但是在这种用法下，Field的作用是限定于整个BaseModel的，无法为每一个属性使用单独的`field`，这时可以采用另外一种方法。
## 2.使用特殊的Pydantic.BaseModel
由于`Pait`的`field`是继承于`pydantic.FieldInfo`，同时也内置了转变为`pydantic.FieldInfo`的方法， 所以在使用的时候可以把上个示例的DemoModel进行转变，
比如对于接口`demo`，DemoModel可以变为如下代码:
```Python
from pait import field

from pydantic import BaseModel

class DemoModel(BaseModel):
    uid: str = field.Query.i(max_length=6, min_length=6, regex="^u")
    name: str = field.Query.i(min_length=4, max_length=10)
    age: int = field.Query.i(ge=0, le=100)
    request_id: str = field.Header.i(default="")
```
这样就可以为每个属性都使用不一样的`field`了，同时还增加了一个`request_id`的属性，它会从Header获取数据，然后接口`demo`需要进行对应的更改，由于DemoModel已经带有了`pait.field`，
所以接口参数不需要按照之前的格式， 可以直接省略`field`的填写， 变为:
```Python
@pait()
async def demo(demo_model: DemoModel) -> JSONResponse:
    return JSONResponse(demo_model.dict())
```
这样`Pait`也能够跟之前一样正确地识别并处理了，在考虑复用后实际的代码可以编写成这样：

```py linenums="1" hl_lines="22-30 33 38"
from typing import Type
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait

from pydantic import BaseModel, ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, ValidationError):
        # 解析Pydantic的抛错
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


def create_demo_model(pait_field: Type[field.BaseRequestResourceField]) -> Type[BaseModel]:
    class DemoModel(BaseModel):
        uid: str = pait_field.i(max_length=6, min_length=6, regex="^u")
        name: str = pait_field.i(min_length=4, max_length=10)
        age: int = pait_field.i(ge=0, le=100)
        request_id: str = field.Header.i(default="")

    return DemoModel


@pait()
async def demo(demo_model: create_demo_model(field.Query)) -> JSONResponse:
    return JSONResponse(demo_model.dict())


@pait()
async def demo1(demo_model: create_demo_model(field.Body)) -> JSONResponse:
    return JSONResponse(demo_model.dict())


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"]), Route("/api/demo1", demo1, methods=["POST"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
由于要支持复用，在22行使用函数`create_demo_model`来根据传入的`pait.field`创建DemoModel，然后34行和39行的接口函数进行对应的更改，
最后使用`curl`进行调用发现响应的结果是正常的：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=u12345&name=so1n&age=10"
{"uid":"u12345","name":"so1n","age":10, "request_id": ""}
➜  ~ curl "http://127.0.0.1:8000/api/demo1" -X POST -d '{"uid": "u12345", "name": "so1n", "age": 10}' --header "Content-Type: application/json"
{"uid":"u12345","name":"so1n","age":10, "request_id": ""}
```
而且这样编写的代码能针对每个属性进行单独地校验，比如传入了不合法的参数，`Pait`仍然可以把参数交给pydantic校验并把错误抛出来：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=12345&name=so1&age=-1"
{
    "data": [
        {
            "loc": [
                "uid"
            ],
            "msg": "ensure this value has at least 6 characters",
            "type": "value_error.any_str.min_length",
            "ctx": {
                "limit_value": 6
            }
        },
        {
            "loc": [
                "name"
            ],
            "msg": "ensure this value has at least 4 characters",
            "type": "value_error.any_str.min_length",
            "ctx": {
                "limit_value": 4
            }
        },
        {
            "loc": [
                "age"
            ],
            "msg": "ensure this value is greater than or equal to 0",
            "type": "value_error.number.not_ge",
            "ctx": {
                "limit_value": 0
            }
        }
    ]
}
```
## 3.其它
### 3.1.Request对象
在使用`Pait`时，`Request`对象使用的频率会大幅的降低，所以`Pait`会自动把`Request`对象进行省略，比如原本的`Starlette`的接口写法是：
```Python
from starlette.requests import Request


async def demo(request: Request):
    pass
```
而在使用了`Pait`后会变为如下代码：
```Python
from pait.app.starlette import pait


@pait()
async def demo():
    pass
```
这时，如果开发者需要`Request`对象或者使用了`Sanic`框架，它不支持函数签名为空的路由函数，则任然可以使用框架原本的方法来获取`Request`对象，
不过`Pait`会要求填写的`Type`必须是`Request`对象的`Type`，才会正确的赋值对应的`Request`对象，比如在`starlette`框架获取`Request`对象的代码如下：
```Python
from pait.app.starlette import pait
from starlette.requests import Request


@pait()
async def demo(request: Request):
    pass
```
### 3.2.如何自定义符合Pydantic校验的Type
前面提到，在`Pait`中`Type`跟Pydantic的`Type`是一样的，这也意味着可以通过`Type`拓展校验规则来弥补`field`的不足，
比如在一个用户可能分布在不同国家的业务中，我们通常会选用时间戳来做时间传递，防止时区不同带来的数据错误，这时代码可以写为：
```py hl_lines="12"
import datetime
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


@pait()
async def demo(timestamp: datetime.datetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])


uvicorn.run(app)
```
不过在运行代码后使用curl调用可以发现，`Pydantic`自动把时间转为datetime类型了，且时区是UTC时区：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T12:26:40+00:00"}
```
这种处理方式是没问题的，但假设这个业务的数据库的服务器是位于某个非UTC时区，数据库与程序的时区都依赖于机器的时区，这样开发者在每次获取数据后还需要再转化一次参数的时区， 很麻烦， 这时可以采用编写一个符合`Pydantic`校验的Type类来解决。

一个符合`Pydantic`校验方法的类必须满足带有`__get_validators__`类方法，且该方法返回一个生成器，
于是可以自己这样实现一个时间戳的转换方法，使Pydantic在遇到时间戳时，能把时间转为`datetime`且该值得时区为服务器的时区：
```Python
import datetime
from typing import Callable, Generator


class UnixDatetime(datetime.datetime):

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(v)
```
然后把这个类应用到我们的代码中：
```py hl_lines="12-22 26"
import datetime
from typing import Callable, Generator, Union
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait import field
from pait.app.starlette import pait


class UnixDatetime(datetime.datetime):

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[int, str]) -> datetime.datetime:
        if not isinstance(v, int):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)


@pait()
async def demo(timestamp: UnixDatetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])


uvicorn.run(app)
```
重新运行这份代码后使用`curl`命令进行测试， 发现返回的时间值已经没有带时区了：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T20:26:40"}
```
