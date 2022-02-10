# 介绍
`Pait`是一个轻量级的Python Api开发工具，拥有参数类型检查, 类型转换和提供文档输出等功能，非常适合用于后端的接口开发，
它被设计兼容多个Python的Web应用开发框架(目前适配了`Flask`, `Starlette`, `Sanic`, `Tornado`)，且做到尽量少地侵入原有框架，`Pait`设计灵感见文章[《给python接口加上一层类型检》](https://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)
。

> NOTE:
>
> mypy check 100%
>
> test coverage 95%+ (排除api_doc)
>
> python version >= 3.7 (支持延迟注释)
>
> 以下代码没有特别说明, 都默认以starlette框架为例


# 功能
 - [x] 参数校验和自动转化(参数校验依赖于`Pydantic`)
 - [x] 参数关系依赖校验
 - [x] 自动生成openapi文件
 - [x] 支持swagger,redoc路由
 - [x] 支持mock响应
 - [x] TestClient支持, 支持测试用例的响应结果校验
 - [x] 支持插件拓展
 - [ ] 本地api文档管理

# 要求
Python3.7+

在项目中使用TypeHints

# 安装
```bash
pip3 install pait
```

# 示例
## 参数校验与文档生成
`Pait`使用方法很简单， 以`starlette`框架为例子：
``` py hl_lines="24 26 27"
from typing import Type
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait, add_doc_route
from pait.field import Body
from pait.model.response import PaitResponseModel
from pydantic import BaseModel, Field


class DemoResponseModel(PaitResponseModel):
    """响应结构体模型，可以供Pait使用"""
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


# 使用pait装饰器装饰函数
@pait(response_model_list=[DemoResponseModel])
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    # 获取对应的值进行返回
    return JSONResponse({'uid': uid, 'user_name': user_name})


app = Starlette(routes=[Route('/api', demo_post, methods=['POST'])])
# 注册OpenAPI接口
add_doc_route(app)
uvicorn.run(app)
```
只需要添加高亮部分的代码，就完成了一个简单的接口，接着运行代码，并在浏览器访问: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger) ,可以看到有个SwaggerUI的页面，目前有两组接口：

![](https://github.com/so1n/so1n_blog_photo/blob/master/blog_photo/Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E9%A6%96%E9%A1%B5.png?raw=true)

其中一组是`Pait doc`自带的3个接口，另外一组是`default`，里面有我们刚创建的`/api`接口，点开`/api`接口，然后会弹出该接口的详情：

![](https://github.com/so1n/so1n_blog_photo/blob/master/blog_photo/Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-api%E6%8E%A5%E5%8F%A3.png?raw=true)

详情里的数据是由`Pait`通过读取函数签名以及传入的`DemoResponseModel`生成的， 接着可以点击`try it out`，并输入参数并点击`Excute`，既可以看到Curl命令生成结果以及服务器响应结果:

![](https://github.com/so1n/so1n_blog_photo/blob/master/blog_photo/Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E8%AF%B7%E6%B1%82.png?raw=true)

从结果可以看出，路由函数正常工作，而路由函数的参数是`Pait`自动从Json Body中提取uid和user_name的值并传入的。

## 插件
除了参数校验和文档生成外，`Pait`还拥有一个插件系统，通过插件系统可以拓展其它功能，比如Mock响应功能，它能根据ResponseModel来自动返回数据，即使这个路由没有数据返回，比如下面的代码：
```py hl_lines="8 11 18 27"
from typing import Type
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait, add_doc_route
from pait.app.starlette.plugin.mock_response import MockAsyncPlugin
from pait.field import Body
from pait.model.response import PaitResponseModel
from pait.plugin import PluginManager
from pydantic import BaseModel, Field


class DemoResponseModel(PaitResponseModel):
    """响应结构体模型，可以供Pait使用"""
    class ResponseModel(BaseModel):
        uid: int = Field(example=999)
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


# 使用pait装饰器装饰函数
@pait(
    post_plugin_list=[PluginManager(MockAsyncPlugin)],
    response_model_list=[DemoResponseModel]
)
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    pass


app = Starlette(routes=[Route('/api', demo_post, methods=['POST'])])
# 注册OpenAPI接口
add_doc_route(app)
uvicorn.run(app)
```
该代码是根据上面的代码进行更改，它移除了返回响应，同时引入了高亮部分的代码，其中第18行中的`uid: int = Field(example=999)`指定了了example值为999，接着运行代码，并运行上面Swagger返回的`Curl`命令:
```bash
➜  ~ curl -X 'POST' \
  'http://127.0.0.1:8000/api' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "uid": 666,
  "user_name": "so1n"
}'
{"uid":999,"user_name":""}
```
可以看到，该接口仍然可以返回响应，该响应是由Mock插件自动生成的，响应中`uid`的值是999，与我们代码中`uid: int = Field(example=999)`设定的值一致，而`user_name`的值则是默认的空字符串。


除此之外，`Pait`还有其它的插件和其它功能，将在后续的文档中详细介绍。

# 性能
`Pait`基于`Python`自带的`inspect`实现函数签名提取， 基于`Pydantic`实现参数校验和类型转换，所以`Pait`的性能表现十分优越。不过目前的`Pait`还在成长中， 还有许多需要优化的地方。

# 使用示例
`Pait`针对每一个支持的Web框架都有完善的代码示例， 可以通过访问示例代码了解最佳实践:

- [flask example](https://github.com/so1n/pait/blob/master/example/param_verify/flask_example.py)

- [sanic example](https://github.com/so1n/pait/blob/master/example/param_verify/sanic_example.py)

- [starlette example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)

- [tornado example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)
