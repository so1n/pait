目前API接口用的最多的序列化方式就是Json，所以基于Json响应有很多特别的需求，目前，`Pait`自带了两个与Json响应相关的插件，他们都用到了`Pait`装饰器填写的`response_model_list`。


!!! note
    - 1.由于要获取到返回的结果，所以这两个插件都会侵入到原有框架，导致使用方法与原有框架有些不同。
    - 2.这两个插件都要单独根据不同的Web框架进行兼容，所以请使用`from pait.app.{web framework name}.plugin.{plugin name} import xxx`引入对应的插件。

## 校验Json响应结果插件
校验Json响应结果插件的主要功能是在收到返回响应结果时，对响应结果进行校验，如果校验成功，才会返回响应，否则就会报错。
以[example.param_verify.starlette_example.async_check_json_plugin_route](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py#L590)为例子：
```py linenums="1"
from typing import Optional
from typing_extensions import TypedDict  # 对于Python3.8以下的只能通过typing_extensions引入
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException
from pait.plugin import PluginManager
from pait.app.starlette.plugin.check_json_resp import AsyncCheckJsonRespPlugin
from example.param_verify.model import UserSuccessRespModel3

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """插件校验不通过会直接抛出异常，该函数会提取异常信息，并以返回对应的错误信息"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


_sub_typed_dict = TypedDict(
    "_sub_typed_dict",
    {
        "uid": int,
        "user_name": str,
        "email": str,
    },
)
_typed_dict = TypedDict(
    "_typed_dict",
    {
        "code": int,
        "msg": str,
        "data": _sub_typed_dict,
    },
)


@pait(response_model_list=[UserSuccessRespModel3], plugin_list=[PluginManager(AsyncCheckJsonRespPlugin)])
async def demo(
    uid: int = field.Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = field.Query.i(default="example@xxx.com", description="user email"),
    user_name: str = field.Query.i(description="user name", min_length=2, max_length=4),
    age: int = field.Query.i(description="age", gt=1, lt=100),
    display_age: int = field.Query.i(0, description="display_age"),
) -> _typed_dict:
    """Test json plugin by resp type is typed dict"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict  # type: ignore


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
在这个代码中，首先是在24-39行定义了一个名为`_typed_dict`类型，他的结构与`UserSuccessRespModel3.response_data`一样，
这个数据结构会在`demo`函数中使用，定义`demo`函数的返回类型为 `_typed_dict`。

!!! note
    如果觉得重复定义会比较麻烦，可以直接填写为`dict`， 但是这样在编写代码时类型检查工具就没办法检查返回的数据结构是否正确了。

然后在42行中引入了一个名为`AsyncCheckJsonRespPlugin`的插件，该插件会在启动的时候检查定义的返回类型与`UserSuccessRespModel3.response_data`是否一致，不一致则会报错。
然后它在运行时校验路由函数响应的字典结构中每个字段的类型是否与`UserSuccessRespModel3.response_data`一致，如果校验失败则返回错误，校验成功则调用框架对应的Json响应对象把数据返回给客户端。
具体示例如下：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18
{"data":"1 validation error for ResponseModel\ndata -> age\n  field required (type=value_error.missing)"}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"","data":{"uid":123,"user_name":"so1n","email":"example@xxx.com","age":18}}%
```
通过结果可以发现，当响应结果与定义的响应Model不匹配时，会直接抛出错误，匹配则正常响应。

## 自动补全Json响应结果插件
在编写API接口的时候，接口返回的响应结果应该会与文档描述的保持一致，但可能会因为一些筛选条件的不同经常导致返回的响应结果是文档描述的响应结果的子集，这种情况下如果客户端没有做特殊处理就会抛出异常，这时可以采用自动补全Json响应结果插件，自动为那些缺少的字段补上默认值。

以上面的代码为例子，去掉变量`_typed_dict`，再把插件`AsyncCheckJsonRespPlugin`替换为`AsyncAutoCompleteJsonRespPlugin`，代码如下:
```py hl_lines="23-26"
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException
from pait.plugin import PluginManager
from pait.app.starlette.plugin.auto_complete_json_resp import AsyncAutoCompleteJsonRespPlugin
from example.param_verify.model import UserSuccessRespModel3

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait(
    response_model_list=[UserSuccessRespModel3],
    plugin_list=[PluginManager(AsyncAutoCompleteJsonRespPlugin)]
)
async def demo(
    uid: int = field.Query.i(description="user id", gt=10, lt=1000),
    email: Optional[str] = field.Query.i(default="example@xxx.com", description="user email"),
    user_name: str = field.Query.i(description="user name", min_length=2, max_length=4),
    age: int = field.Query.i(description="age", gt=1, lt=100),
    display_age: int = field.Query.i(0, description="display_age"),
) -> dict:
    """Test json plugin by resp type is typed dict"""
    return_dict: dict = {
        "code": 0,
        "msg": "",
        "data": {
            "uid": uid,
            "user_name": user_name,
            "email": email,
        },
    }
    if display_age == 1:
        return_dict["data"]["age"] = age
    return return_dict  # type: ignore


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
接着在运行与上面例子相同的请求:
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"","data":{"uid":123,"user_name":"so1n","age":18,"email":"example@xxx.com"}}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18
{"code":0,"msg":"","data":{"uid":123,"user_name":"so1n","age":0,"email":"example@xxx.com"}}%
```
通过响应结果可以发现，对于第一个响应结果的`age`值为调用命令时填写的18，而第二个响应结果中本来是没有`age`字段的，该字段值是由插件`AsyncAutoCompleteJsonRespPlugin`根据`age`的类型自动填上的,2k默认值0。

`AsyncAutoCompleteJsonRespPlugin`自动补全的原理从`response_model_list`中选出开发者填写的第一个`ResponseModel`，比如代码中的例子就是`UserSuccessRespModel3`，
然后通过调用`UserSuccessRespModel3`的`get_default_dict`获取到对应的默认值，再与路由函数返回的数据结构进行对比，如果发现响应的数据结构缺少对应的字段，就会自动补上。
如果开发者觉得自动生成的默认值不喜欢，那么可以通过字段对应的`Field`来指定自己想要的默认值，比如对`UserSuccessRespModel3`进行更改:
```py hl_lines="8"
class UserSuccessRespModel3(PaitJsonResponseModel):
    is_core: bool = True

    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000)
            user_name: str = Field(description="user name", min_length=2, max_length=4)
            age: int = Field(default=10, description="age", gt=1, lt=100)
            email: str = Field(description="user email")

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel
```
通过`Field`定义`age`的默认值为10,再运行一样的请求后可以可以发现，返回的`age`默认值变为10：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"","data":{"uid":123,"user_name":"so1n","age":18,"email":"example@xxx.com"}}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18
{"code":0,"msg":"","data":{"uid":123,"user_name":"so1n","age":10,"email":"example@xxx.com"}}%
```
