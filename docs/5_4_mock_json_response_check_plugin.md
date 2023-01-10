在对接了需求后，我们需要先出一份接口文档给客户端后再编写接口对应的逻辑代码，这时就可以使用`Pait`来装饰一个没有逻辑功能的路由函数，
并通过`Pait`自动生成一份API文档给客户端使用，然后双方再一起开发功能。

但是在没达到联调之前客户端开发者也需要进行一些测试，一般情况下客户端需要先根据响应Model来编写对应的Mock数据，
这样会增加前端的工作量，同时前端Mock的数据并不一定是我们想要的，这时可以使用`MockPlugin`插件来让接口提供Mock数据。

`MockPlugin`插件使用非常简单，代码如下:

```py hl_lines="15-18"
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException
from pait.app.starlette.plugin.mock_response import MockPlugin
from example.common import UserSuccessRespModel3

from pait.app.starlette import pait
from pait import field


@pait(
    response_model_list=[UserSuccessRespModel3],
    plugin_list=[MockPlugin.build()]
)
async def demo(
        uid: int = field.Query.i(description="user id", gt=10, lt=1000),
        email: Optional[str] = field.Query.i(default="example@xxx.com", description="user email"),
        user_name: str = field.Query.i(description="user name", min_length=2, max_length=4),
        age: int = field.Query.i(description="age", gt=1, lt=100),
        display_age: int = field.Query.i(0, description="display_age"),
) -> dict:
    pass


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
uvicorn.run(app)
```
这份代码中，开发者实现了一个路由函数签名，该函数没有任何逻辑，然后通过`pait`装饰器填写`MockPlugin`和ResponseModel，
如果有多个ResponseModel的话`MockPlugin`会默认使用第一个ResponseModel，运行这份代码后执行对应的请求命令可以得到默认的Mock响应：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"success","data":{"uid":0,"user_name":"","age":0,"email":""}}%
```
这份默认的响应数据是`MockPlugin`通过调用`UserSuccessRespModel3.get_example_value`生成的，如果对于生成的默认值不满意，
可以通过`Field`的`example`来定义不同的响应值，比如把`UserSuccessRespModel3`改成下面的样子：
```py
import random
# 引入faker库
from faker import Faker

fake = Faker()


class UserSuccessRespModel3(PaitJsonResponseModel):
    is_core: bool = True

    class ResponseModel(ResponseModel):  # type: ignore
        class DataModel(BaseModel):
            uid: int = Field(description="user id", gt=10, lt=1000, example=lambda :random.randint(100000, 900000))
            user_name: str = Field(description="user name", min_length=2, max_length=4, example="so1n")
            age: int = Field(description="age", gt=1, lt=100, example=18)
            email: str = Field(description="user email", example=fake.email)

        data: DataModel

    description: str = "success response"
    response_data: Type[BaseModel] = ResponseModel
```
这样一来每个字段都有自己的一套生成示例值的规则，比如字段uid就是随机从100000-900000中挑选一个值，字段eamil就是通过fake.email生成的，而字段user_name和age则有指定的固定值，
通过运行代码后执行请求命令可以发现，返回的示例值符合我们的定义:
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"success","data":{"uid":835740,"user_name":"so1n","age":18,"email":"warnold@example.net"}}
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"success","data":{"uid":203363,"user_name":"so1n","age":18,"email":"nathanthomas@example.net"}}
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code":0,"msg":"success","data":{"uid":508769,"user_name":"so1n","age":18,"email":"reynoldslisa@example.com"}}
```
