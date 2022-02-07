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
`Pait`是一个辅助框架， 在介绍`Pait`使用方法之前， 先看看原本框架的实现代码，该代码是一个普通的`POST`接口， 该接口会校验和转行参数， 并返回给调用端：
```Python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def demo_post(request: Request) -> JSONResponse:
    body_dict: dict = await request.json()
    uid: int = body_dict.get('uid', 0)
    user_name: str = body_dict.get('user_name', "")
    # 以下代码只是作为示范, 一般情况下, 我们都会做一些封装, 不会显得过于冗余
    if not uid:
        raise ValueError('xxx')
    if type(uid) != int:
        raise TypeError('xxxx')
    if 10 <= uid <= 1000:
        raise ValueError('xxx')

    if not user_name:
        raise ValueError('xxx')
    if type(user_name) != str:
        raise TypeError('xxxx')
    if 2 <= len(user_name) <= 4:
        raise ValueError('xxx')

    return JSONResponse(
        {
            'result': {
                'uid': body_dict['uid'],
                'user_name': body_dict['user_name']
            }
        }
    )


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
可以看出这种写法非常麻烦， 而在使用了`Pait`后， 代码可以变得比较精炼， 其中高亮部分则与`Pait`相关：
``` py hl_lines="11 13 14"
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


# 使用pait装饰器装饰函数
@pait()
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    # 获取对应的值进行返回
    return JSONResponse({'result': {'uid': uid, 'user_name': user_name}})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
```

# 性能
`Pait`基于`Python`自带的`inspect`实现函数签名提取， 基于`Pydantic`实现参数校验和类型转换，所以`Pait`的性能表现十分优越。不过目前的`Pait`还在成长中， 还有许多需要优化的地方。

# 示例
`Pait`针对每一个支持的Web框架都有完善的代码示例， 可以通过访问示例代码了解最佳实践:

- [flask example](https://github.com/so1n/pait/blob/master/example/param_verify/flask_example.py)

- [sanic example](https://github.com/so1n/pait/blob/master/example/param_verify/sanic_example.py)

- [starlette example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)

- [tornado example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)
