## 1.介绍
`Pait`会在运行时自动捕获路由函数的请求参数和url，method等信息自动生成OpenAPI数据, 不过单靠函数的信息还不够，还需要开发者手动标注一些相关信息, 如下面的例子:

```Python
from example.common import FailRespModel, UserSuccessRespModel
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
- response_model_list: 返回的结果数据, 需要继承于`pait.model.PaitResponseModel`.由于`pait`是web框架的拓展插件,不会修改框架的代码, 所以该参数不会与接口生成的响应进行校验(也不应该用于生产环境), 目前只会用于文档生成，mock响应生成，TestClient校验等。
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


## 2.OpenAPI
通过用户手动补齐这些数据后，`Pait`就能生成一份完整的OpenAPI文档， 目前`Pait`支持OpenAPI的大多数功能,少数未实现的功能将通过迭代逐步完善，目前支持的参数如下(下一个版本会提供更多的参数):

- title: `OpenAPI`的title
- open_api_info: `OpenAPI` info的参数
- open_api_tag_list: `OpenAPI` tag的相关描述
- open_api_server_list: `OpenAPI` server 列表
- type_: 输出的OpenAPI文件类型, 可选json和yaml
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

from pait.openapi.openapi import OpenAPI
from pait.app.starlette import load_app

# 提取路由信息到pait的数据模块
pait_dict = load_app(app)
# 根据数据模块的数据生成路由的OpenAPI
OpenAPI(pait_dict).content()
```
通过改代码就可以自动生成一个OpenAPI的文件，不过一般情况下都很少直接使用生成的OpenAPI文件，如果单纯的需要一份API文档，那么可以使用自带的`markdown`模块来生成接口对应的`markdown`文档，代码如下：

```Python
from any_api.openapi.to.markdown import Markdown
from pait.openapi.openapi import OpenAPI

print(Markdown(OpenAPI(pait_dict)).content)
```

## 3.OpenAPI路由
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
通过`add_doc_route`函数，用户就可以调用`http://127.0.0.1/swagger`访问对应的Swagger页面，得到首页类型的API文档页面，不过`add_doc_route`函数支持其它参数，具体如下：
```Python
# 把路由注入到app中, 并且以/doc为前缀
add_doc_route(app, prefix='/doc')
# 通常挂在Nginx后面的应用程序可能无法知道当前请求的scheme是https还是http，可以通过scheme指定请求点scheme
add_doc_route(app, scheme='https')
# 通常不适合把接口文档暴露给外面的用户使用，目前支持`pin_code`参数来增加一点点安全性，
# 比如如下定义后，只能通过http://127.0.0.1/swagger?pin-code=6666才能成功访问Swagger页面
add_doc_route(app, pin_code='6666')

if __name__ == "__main__":
    uvicorn.run(app, log_level="debug")
```

### 3.1.OpenAPI路由的模板变量
在编写API接口时，大部分接口都是需要登录的，也就是需要带上Token参数，如果每次都是从数据库查出对应的Token再粘贴会非常的麻烦，这时就可以使用模板变量，让`Pait`帮助用户自动填写变量的值，以上面的代码为例子，为其中的uid引入对应的模板变量，代码如下：
```py hl_lines="10 15"
import uvicorn  # type: ignore
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# 引入add_doc_route, 针对每个框架都有一个具体的实现
from pait.app.starlette import add_doc_route, pait
from pait.field import Body
from pait.model.template import TemplateVar


# 创建一个基于Pydantic.BaseModel的Model
class UserModel(BaseModel):
    uid: int = Field(description="user id", gt=10, lt=1000, example=TemplateVar("uid"))
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

if __name__ == "__main__":
    uvicorn.run(app, log_level="debug")
```
这段代码通过第一段高亮引入了一个`TemplateVar`类，接着在第二段高亮中，uid的Field的example属性被填写`TemplateVar("uid")`，之后在运行的时候`Pait`就知道参数`uid`的模板变量为`uid`。

现在运行上面的代码，并在浏览器输入`http://127.0.0.1:8000/swagger?template-uid=123`，打开后可以看到如下图:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16506183174491650618317309.png)

通过图可以发现输入的123被设置到对应的参数中，而不是默认的0了。`Pait`之所以能把用户的值设置到对应的参数中是因为这个url多了一段`template-uid=123`，这样一来OpenAPI路由在收到对应的请求在发现请求携带了一个以`template-`开头的变量，知道这是用户为模板变量`uid`指定了对应的值，于是在生成OpenAPI数据时，会自动帮模板变量为uid的参数附上用户的值。
