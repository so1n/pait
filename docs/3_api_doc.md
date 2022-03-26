## 1.介绍
`Pait`会在运行时自动捕获路由函数的请求参数和url,method等信息自动生成OpenAPI数据, 不过单靠函数的信息还不够，还需要开发者手动标注一些相关信息, 如下面的例子:
```Python
from example.param_verify.model import FailRespModel, UserSuccessRespModel
from pait.app.starlette import pait
from pait.model.status import PaitStatus


@pait(
  author=("so1n",),
  group="user",
  status=PaitStatus.release,
  tag=("user", "post"),
  response_model_list=[UserSuccessRespModel, FailRespModel],
)
def demo() -> None:
    pass
```
这个例子增加了`author`,`group`,`status`等标注，具体的标注作用如下:

- author: 编写接口的作者列表
- group: 接口所属的组(该选项目前不会用于OpenAPI)
- tag: 接口的标签
- response_model_list: 返回的结果数据, 需要继承于`pait.model.PaitResponseModel`.由于`pait`是web框架的拓展,不会修改框架的代码, 所以该参数不会用于普通的请求判断(也不应该用于生产环境), 目前只会用于文档生成, mock响应生成, TestClient校验。
- status: 接口的状态, 目前只支持PaitStatus的几种状态(该选项只有下线相关的才会用于OpenAPI并标注为弃用)

    * 默认状态:
        - undefined: 未定义, 默认状态
    * 开发中:
        - design: 设计中
        - dev: 开发测试中
    * 开发完成:
        - integration: 联调
        - complete: 开发完成
        - test: 测试中
    * 上线:
        - release: 上线
    * 下线:
        - abnormal: 出现异常, 下线
        - maintenance: 维护中
        - archive: 归档
        - abandoned: 遗弃


## OpenAPI
通过这些数据后，`Pait`就能生成一份完整的OpenAPI文档， 目前`Pait`支持OpenAPI的大多数功能,少数未实现的功能将通过迭代逐步完善，目前支持的参数如下(下一个版本会提供更多的参数):

- title: `OpenAPI`的title
- open_api_info: `OpenAPI` info的参数
- open_api_tag_list: `OpenAPI` tag的相关描述
- open_api_server_list: `OpenAPI` server 列表
- type_: 输出的类型, 可选json和yaml
- filename: 输出文件名, 如果为空则输出到终端

以下是OpenAPI文档输出的示例代码:

```Python
from pydantic import BaseModel, conint, constr
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


# 创建一个基于Pydantic.BaseModel的Model
class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)  # 自动校验类型是否为int,且是否大于10小于1000
    user_name: constr(min_length=2, max_length=4)  # 自动校验类型是否为str, 且长度是否大于等于2,小于等于4


# 使用pait装饰器装饰函数
@pait()
async def demo_post(
        # pait通过Body()知道当前需要从请求中获取body的值,并赋值到model中,
        # 而这个model的结构正是上面的PydanticModel,他会根据我们定义的字段自动获取值并进行转换和判断
        model: PydanticModel = Body.i()
):
    # 获取对应的值进行返回
    return JSONResponse({'result': model.dict()})


app = Starlette(routes=[Route('/api', demo_post, methods=['POST'])])

from pait.api_doc.open_api import PaitOpenAPI
from pait.app.starlette import load_app

# 提取路由信息到pait的数据模块
pait_dict = load_app(app)
# 根据数据模块的数据生成路由的OpenAPI
PaitOpenAPI(pait_dict)
```
此外，如果单纯的需要一份API文档，那么可以使用自带的`markdown`模块来生成接口对应的`markdown`文档：
```Python
from pait.api_doc.markdown import PaitMd

PaitMd(pait_dict)
```

## OpenAPI路由
如文档首页示例，`Pait`还支持OpenAPI路由, 同时支持`Redoc`和`Swagger`的页面展示, 而这些只需要调用`add_doc_route`函数即可为`app`实例增加三个路由:

- `/openapi.json`  获取OpenAPI的json响应
- /redoc           使用`Redoc`展示接口文档数据
- /swagger         使用`Swagger`展示接口文档数据

具体例子如下:
```Python3
import uvicorn  # type: ignore
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# 引入add_doc_route, 针对每个框架都有一个具体的实现
from pait.app.starlette import add_doc_route, pait
from pait.field import Body


# 创建一个基于Pydantic.BaseModel的Model
class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000)
    user_name: str = Field(description="user name", min_length=2, max_length=4)


# 使用pait装饰器装饰函数
@pait()
async def demo_post(
    # pait通过Body()知道当前需要从请求中获取body的值,并赋值到model中,
    # 而这个model的结构正是上面的PydanticModel,他会根据我们定义的字段自动获取值并进行转换和判断
    model: UserModel = Body.i()  # 使用i函数可以解决mypy类型校验的问题
) -> JSONResponse:
    # 获取对应的值进行返回
    return JSONResponse({'result': model.dict()})


app = Starlette(routes=[Route('/api', demo_post, methods=['POST'])])
# 把路由注入到app中
add_doc_route(app)
```

此外，`add_doc_route`函数支持其它参数，具体如下：
```Python
# 把路由注入到app中, 并且以/doc为前缀
add_doc_route(app, prefix='/doc')
# 通常挂在Nginx后面的应用程序可能无法知道当前请求的scheme是https还是http，可以通过scheme指定请求点scheme
add_doc_route(app, scheme='https')
# 通常不适合把接口文档暴露给外面的用户使用，目前支持`pin_code`参数来增加一点点安全性，
# 比如如下定义后，只能通过http://127.0.0.1/swagger?pin_code=6666才能成功访问Swagger页面
add_doc_route(app, pin_code='6666')
```
