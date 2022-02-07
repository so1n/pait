`field`在`Pait`中起到了至关重要的作用， `Pait`除了使用`field`用于获取数据来源外， 还通过它实现了很多其它的功能， 在本章中只着重说明参数校验这一块。

## 1.Field的种类

除了上文提到的Body外， `Field`还拥有其它的种类， 它们的名称和作用如下:

- Body: 获取当前请求的Json数据
- Cookie: 获取当前请求的Cookie数据(注意， 目前Cookie数据会被转化为一个Python字典， 这意味着Cookie的Key不能重复。同时， 在Field为Cookie时， type最好是str)
- File：获取当前请求的file对象，该对象与原文Web框架的file对象一致
- Form：获取当前请求的form数据，如果有多个重复Key，只会返回第一个值
- Header: 获取当前请求的header数据
- Path: 获取当前请求的path数据，如`/api/{version}/test`，则会获取到version的数据
- Query: 获取当前请求的Url参数对应的数据，如果有多个重复Key，只会返回第一个值
- MultiForm：获取当前请求的form数据， 返回Key对应的数据列表
- MultiQuery：获取当前请求的Url参数对应的数据， 返回Key对应的数据列表

各个种类的具体使用方法很简单，只要填入`<name>:<type>=<default>`中的`default`位置即可，以这段代码为例子(为了确保能复制粘贴后运行，没有演示field.File):
```Python
from typing import List, Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field

@pait()
async def demo(
    form_a: str = field.Form.i(),
    form_b: str = field.Form.i(),
    multi_form_c: List[str] = field.MultiForm.i(),
    cookie: dict = field.Cookie.i(raw_return=True),
    multi_user_name: List[str] = field.MultiQuery.i(min_length=2, max_length=4),
    age: int = field.Path.i(gt=1, lt=100),
    uid: int = field.Query.i(gt=10, lt=1000),
    user_name: str = field.Query.i(min_length=2, max_length=4),
    email: Optional[str] = field.Query.i(default="example@xxx.com"),
    accept: str = field.Header.i()
) -> JSONResponse:
    """Test the use of all BaseField-based"""
    return JSONResponse(
        {
            "code": 0,
            "msg": "",
            "data": {
                "accept": accept,
                "form_a": form_a,
                "form_b": form_b,
                "form_c": multi_form_c,
                "cookie": cookie,
                "multi_user_name": multi_user_name,
                "age": age,
                "uid": uid,
                "user_name": user_name,
                "email": email,
            },
        }
    )

app = Starlette(
    routes=[
        Route("/api/demo/{age}", demo, methods=["POST"]),
    ]
)


uvicorn.run(app)
```
这段代码来自于[pait base field example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py#L163), 并做了一些小改动，该接口的主要责任就是把参数通过json的格式返回给调用者。
接下来使用`curl`命令进行一次请求测试， 通过输出结果可以发现，`Pait`都能通过`field`的种类准确的拿到对应的值， 并赋值到变量中。
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/demo/12?uid=99&user_name=so1n&multi_user_name=so1n' \
  -H 'accept: application/json' \
  -H 'Cookie: cookie=cookie=test cookie' \
  -H 'Content-Type: multipart/form-data' \
  -F 'form_a=a' \
  -F 'form_b=b' \
  -F 'multi_form_c=string,string'

{
    "code": 0,
    "msg": "",
    "data": {
        "accept": "application/json",
        "form_a": "a",
        "form_b": "b",
        "form_c": [
            "string,string"
        ],
        "cookie": {
            "cookie": "cookie=test cookie"
        },
        "multi_user_name": [
            "so1n"
        ],
        "age": 12,
        "uid": 99,
        "user_name": "so1n",
        "email": "example@xxx.com"
    }
}
```
## 2.Field的功能
从上面的例子可以看到， 请求中没有带上`email`参数， 但是该接口任然可以得到`email`的值`example@xxx.com`，
这是因为在填写`email`的`field`时，我把`example@xxx.com`填写到default值中，这样`Pait`会在获取不到该变量的对应值的情况下，`也能把默认值赋给对应的变量。

除了默认值之外， `field`也有很多的功能，这些功能大部分来源于`field`所继承的`pydantic.Field`。


### 2.1.default
`Pait`通过该参数支持默认值， 如果没有默认值可以直接不填写该参数的值。

示例代码如下，两个接口都直接返回获取到的值`demo_value`，其中`demo`接口带有默认值， 默认值为字符串123，而`demo1`接口没有默认值:
```py hl_lines="20 25"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException


async def api_exception(request: Request, exc: Exception) -> PlainTextResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return PlainTextResponse(str(exc))


@pait()
async def demo(demo_value: str = field.Query.i(default="123")) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


@pait()
async def demo1(demo_value: str = field.Query.i()) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
        Route("/api/demo1", demo1, methods=["GET"]),
    ]
)

app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
使用`curl`调用可以发现，对于有默认值得接口`/api/demo`，当没有传参数demo_value时，默认返回123, 传参数456时，返回值是456:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
123
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=456"
456
```
而没有带参数的请求会看到有个报错， 提示没有找到`demo_value`的值:
```bash
➜  curl "http://127.0.0.1:8000/api/demo1"
Can not found demo_value value
```

### 2.2.default_factory
该参数用于默认值是函数的情况，可以用来填写类似于`datetime.datetime.now`的默认值。

示例代码如下，第一个接口的默认值是当前时间， 第二个接口的默认值是uuid，他们每次调用段返回值都是收到请求时生成的:
```py hl_lines="14 20"
import datetime
import uuid
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    now: datetime.datetime = field.Query.i(default_factory=datetime.datetime.now)
) -> PlainTextResponse:
    return PlainTextResponse(now)


@pait()
async def demo1(demo_value: str = field.Query.i(default_factory=lambda: uuid.uuid4().hex)) -> PlainTextResponse:
    return PlainTextResponse(demo_value)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
        Route("/api/demo1", demo1, methods=["GET"]),
    ]
)

uvicorn.run(app)
```
使用`curl`调用可以发现每次返回的结果都是不一样的:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:29.127519
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:33.789994
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
7e4659e18103471da9db91ed4843d962
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
ef84f04fa9fc4ea9a8b44449c76146b8
```
### 2.3.alias
参数的别名，一些参数可能被命名为`Content-Type`, 但是Python不支持这种命名方式， 此时可以使用别名。

示例代码如下:
```py hl_lines="11"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(content_type: str = field.Header.i(alias="Content-Type")) -> PlainTextResponse:
    return PlainTextResponse(content_type)


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
使用`curl`调用可以发现，`Pait`正常的从Header中提取`Content-Type`的值并赋给了content_type:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -H "Content-Type:123"
123
```

### 2.4.数字校验之gt，ge，lt，le，multiple_of
这几个值都是校验数字是否合法，仅用于数值的类型，他们的作用各不相同：

- gt：仅用于数值的类型，会校验数值是否大于该值，同时也会在OpenAPI添加`exclusiveMinimum`属性。
- ge：仅用于数值的类型，会校验数值是否大于等于该值，同时也会在OpenAPI添加`exclusiveMinimum`属性。
- lt：仅用于数值的类型，会校验数值是否小于该值，同时也会在OpenAPI添加`exclusiveMaximum`属性。
- le：仅用于数值的类型，会校验数值是否小于等于该值，同时也会在OpenAPI添加`exclusiveMaximum`属性。
- multiple_of：仅用于数字， 会校验该数字是否是指定值得倍数。

示例代码如下，这个示例代码只有一个接口，但是接受了三个参数`demo_value1`, `demo_value2`, `demo_value3`，他们分别只接收符合大于1小于10；等于1;3的倍数的三个数：
```py hl_lines="23-25"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, ValidationError):
        # 解析Pydantic的抛错
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value1: int = field.Query.i(gt=1, lt=10),
    demo_value2: int = field.Query.i(ge=1, le=1),
    demo_value3: int = field.Query.i(multiple_of=3),
) -> JSONResponse:
    return JSONResponse({"data": [demo_value1, demo_value2, demo_value3]})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
使用`curl`调用可以发现第一个请求符合要求并得到了想要的响应结果，第二个请求则三个参数都错了，并返回`Pydantic.ValidationError`的错误信息，从错误信息可以简单的看出来三个参数都不符合接口设置的限定条件：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=3"
{"data":[2,1,3]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=11&demo_value2=2&demo_value3=2"
{
    "data": [
        {
            "loc": [
                "demo_value1"
            ],
            "msg": "ensure this value is less than 10",
            "type": "value_error.number.not_lt",
            "ctx": {
                "limit_value": 10
            }
        },
        {
            "loc": [
                "demo_value2"
            ],
            "msg": "ensure this value is less than or equal to 1",
            "type": "value_error.number.not_le",
            "ctx": {
                "limit_value": 1
            }
        },
        {
            "loc": [
                "demo_value3"
            ],
            "msg": "ensure this value is a multiple of 3",
            "type": "value_error.number.not_multiple",
            "ctx": {
                "multiple_of": 3
            }
        }
    ]
}
```
### 2.5.数组校验之min_items，max_items
这几个值都是校验数组是否合法，仅用于数组的类型，他们的作用各不相同：

- min_items：仅用于数组类型，会校验字列表是否满足大于等于指定的值。
- max_items： 仅用于数组类型，会校验字列表是否满足小于等于指定的值。

示例代码如下，该接口通过`field.MultiQuery`从请求Url中获取参数`demo_value`的数组，并返回给调用端，其中数组的长度限定在大于等于1且小于等于2之间：
```py hl_lines="24"
from typing import List
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2)) -> JSONResponse:
    return JSONResponse({"data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
与2.4一样，通过`curl`调用可以发现合法的参数会放行，不合法的参数会抛错：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[1]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2"
{"data":[1,2]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2&demo_value=3"
{
    "data": [
        {
            "loc": [
                "demo_value"
            ],
            "msg": "ensure this value has at most 2 items",
            "type": "value_error.list.max_items",
            "ctx": {
                "limit_value": 2
            }
        }
    ]
}
```
### 2.6.字符串校验之min_length，max_length，regex
这几个值都是校验字符串是否合法，仅用于字符串的类型，他们的作用各不相同：

- min_length：仅用于字符串类型，会校验字符串的长度是否满足大于等于指定的值。
- max_length：仅用于字符串类型，会校验字符串的长度是否满足小于等于指定的值。
- regex：仅用于字符串类型，会校验字符串是否符合该正则表达式。

示例代码如下， 该接口需要从Url中获取一个值， 这个值得长度大小为6，且必须为英文字母u开头：
```py hl_lines="23"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field
from pait.exceptions import TipException
from pydantic import ValidationError


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(demo_value: str = field.Query.i(min_length=6, max_length=6, regex="^u")) -> JSONResponse:
    return JSONResponse({"data": demo_value})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)

uvicorn.run(app)
```
使用`curl`进行三次请求，第一次为正常数据，第二次为不符合正则表达式，第三次为长度不符合：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=u66666"
{"data":"u66666"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=666666"
{"data":[{"loc":["demo_value"],"msg":"string does not match regex \"^u\"","type":"value_error.str.regex","ctx":{"pattern":"^u"}}]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[{"loc":["demo_value"],"msg":"ensure this value has at least 6 characters","type":"value_error.any_str.min_length","ctx":{"limit_value":6}}]}
```
### 2.7.raw_return
该参数的默认值为`False`，如果为`True`，则`Pait`不会根据参数名或者`alias`为key从请求数据获取值， 而是把整个请求值返回给对应的变量。

示例代码如下， 该接口为一个POST接口， 该接口需要两个值，第一个值为整个客户端传过来的Json参数， 而第二个值为客户端传过来的Json参数中Key为a的值：

```py hl_lines="12-13"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    demo_value1: dict = field.Body.i(raw_return=True),
    a: str = field.Body.i(),
) -> JSONResponse:
    return JSONResponse({
        "demo_value": demo_value1,
        "a": a
    })


app = Starlette(routes=[Route("/api/demo", demo, methods=["POST"])])

uvicorn.run(app)
```
使用`curl`调用， 可以发现结果符合预期：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -X POST -d '{"a": "1", "b": "2"}' --header "Content-Type: application/json"
{"demo_value":{"a":"1","b":"2"},"a":"1"}
```

### 2.8.其它功能
除了上述功能外， `Pait`还有其它属性， 但是都只与OpenAPI有关， 所以本章只做简单介绍：

- link：用于支持OpenApi的link功能。
- media_type：Field对应的media_type，用于OpenAPI的Scheme的参数media type分类。
- example：用于文档的示例值，以及Mock请求与响应等Mock功能，同时支持变量和可调用函数如`datetime.datetim.now`，推荐与[faker](https://github.com/joke2k/faker)一起使用。
- openapi_serialization：用于该值在OpenAPI的Schema的序列化方式。
- description: 用于OpenAPI的参数描述
