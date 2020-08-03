## pait
pait是一个可以用于python的api接口工具,也可以认为是python api接口类型(t-- type hints)

pait可以让你的python web框架拥有像fastapi一样的类型检查和类型转换的功能(由pydantic支持)
[了解如何实现类型转换和检查功能](http://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)

## 安装
```bash
pip install pait
```

## 使用
以下代码没有特别说明,都默认使用starletter框架.

### 在路由函数中使用使用pait
先看看普通的路由函数代码:
```Python
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse


async def demo_post(request: Request):
    return JSONResponse({'result': await request.json()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
在使用pait后,路由函数代码为:
```Python
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

# import from pait and pydantic
from pait.field import Body
from pait.web.starletter import params_verify
from pydantic import (
    BaseModel,
    conint,
    constr,
)


# create Pydantic.BaseModel
class PydanticModel(BaseModel):
    uid: conint(gt=10, lt=1000)
    user_name: constr(min_length=2, max_length=4)


# use params_verify in route handle
@params_verify()
async def demo_post(
    # pait knows to get the body data from the request by 'Body' 
    # and assign it to the Pydantic model
    model: PydanticModel = Body()  
):
    # replace body data to dict
    return JSONResponse({'result': model.dict()})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)


uvicorn.run(app)
```
可以看出,只需要对路由函数添加一个`params_verify`装饰器,并把`demo_post`的参数改为`model: PydanticModel = Body()`即可.
pait通过识别`Body`知道需要获取post请求body的数据,并把数据根据`conint(gt=10, lt=1000)`进行转换和限制,并赋值给`PydanticModel`,用户只需要像使用`Pydantic`一样调用`model`即可获取到数据.

这里只是一个简单的demo,上面的参数只使用到一种写法,下面会介绍pait支持的两种写法以及用途.
### pait支持的参数写法
pait为了方便用户使用,支持两种写法,分别为model型和type型:
- model型 
model型的特点是参数的type hints会传入一个继承于`pydantic.BaseModel`的类.pait会把获取的值传入model,并进行类型校验和转换,用户只要像调用`pydantic.BaseModel`的方法一样调用即可.此时用户填写的参数值(`Field`),在初始化时可以填入`key`和`default`,`fix_key`,但是pait只会使用到`fix_key`.
    ```Python
    model: PydanticModel = Body() 
    ```
- type型
type型的特点就是传入的是python的type,typing值以及`pydantic`的类型值.pait内部会把该函数的所有type型参数合成一个`pydantic.BaseModel`,进行类型校验和转换,并把值再重新赋值给各个参数,此时的pait会调用到用户初始化`Field`时填写的`key`,`default`,`fix_key`
    ```Python
    user_agent: str = Header(key='user-agent', default='not_set_ua')
    ```
### Field介绍
在介绍Field的功能之前先看下面的例子, `pait` 会自动从Body数据中获取到uid的数据
```Python
@params_verify()
async def demo_post(
    # get uid from request body data
    uid: int = Body()  
):
    pass
```
如果参数名并不符合Header的key命名,可以使用key参数
```Python
@params_verify()
async def demo_post(
    # get uid from request body data
    uid: int = Body(),
    # get Content-Type from header
    content_type: str = Header(key='Content-Type')
):
    pass
```

上面中用到了field的Body,pait除了Body外还支持多种field,pait通过field知道用户需要获取什么类型的数据.field目前有两种类型,一种是普通型field,另一种是依赖注入型field.

普通型field初始化参数有`key`,`default`,`fix_key`:
- key(只用于type型)  
  一般情况下,当设置field为Field.Header时,pait会获取到当前请求的header数据,并把参数名当做key,但是header的key命名方式与python变量命名不兼容,会导致pait获取不到对应的数据.
  通过下面的例子,把真正的key赋值给初始化的key时,pait会优先选择我们的赋值key去header中获取对应的值
    ```Python
    user_agent: str = Header(key='user-agent', default='not_set_ua')
    ```
- default(只用于type型)
  当pait获取不到对应数据时,会直接引用初始化时的default
- fix_key
  除了使用key参数来解决某些数据的的key与python变量命名冲突外,还可以通过`fix_key=True`来自动解决命名冲突的问题.该方法也是model型命名冲突的唯一解决方案.

以下为简单型field说明:
- Field.Body  获取到当前请求的json数据
- Field.Cookie 获取到当前请求的cookie数据
- Field.File  获取到当前请求的file数据,会根据不同的web框架返回不同的file对象类型
- Field.Form  获取当前请求的表单数据
- Field.Header  获取当前请求的header数据
- Field.Path   获取当前请求的path数据(如/api/{version}/test, 可以获得到version数据)
- Field.Query  获取到当前请求的url参数以及对应数据


依赖注入型field目前只有一个,且由于model写法的存在可以充当部分依赖注入的功能,所以依赖注入型field功能比较简单,只支持在初始化时传入一个函数,并在接收到请求时自动执行该函数.

### requests对象
`Pait` 并不返回requests对象,如果你需要requests对象,那可以填写像`requests: Requests`一样的参数(需要使用TypeHints格式),即可得到web框架对应的requests对象
```Python
from starlette.requests import Request


@params_verify()
async def demo_post(
    request: Requests,
    # get uid from request body data
    uid: int = Body()  
):
    pass
```
### 异常处理
pait并不会为异常进行响应,而是把异常处理交给用户自己处理,正常情况下,pait只会抛出`pydantic`的异常和`PaitException`异常,用户需要自己捕获异常并进行处理,如下所示:
```Python
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from pait.exceptions import PaitException
from pydantic import ValidationError

async def api_exception(request: Request, exc: Exception) -> Response:
    """
    自己处理异常的逻辑    
    """

APP = Starlette()
APP.add_exception_handler(PaitException, api_exception)
APP.add_exception_handler(ValidationError, api_exception)
```

### 异常提示
如果用户错误的使用pait,那Python会报错,但报错信息只说明pait的哪个逻辑运行错误,这样子对于用户排查错误是十分困难的.所以pait对报错进行了处理并做出如下提示,告诉用户是哪个引用到pait的函数出错和出错位置以及出错的参数,如果用户使用类似于`Pycharm`的IDE,还可以点击路径跳转到对应的地方.
```Bash
  File "/home/so1n/github/pait/pait/param_handle.py", line 65, in raise_and_tip
    ) from exception
KeyError: 'File "/home/so1n/github/pait/example/starletter_example.py", line 29, in demo_post2  kwargs param:content_type: <class \'str\'> = Header(key=None, default=None) not found in Headers({\'host\': \'127.0.0.1:8000\', \'user-agent\': \'curl/7.52.1\', \'accept\': \'*/*\', \'content-type\': \'application/json\', \'data_type\': \'msg\', \'content-length\': \'38\'}), try use Header(key={key name})'
```
如果你想查看更多消息,那可以把日志等级设置为debug.
```Python
DEBUG:root:
async def demo_post(
    ...
    content_type: <class 'str'> = Header(key=None, default=None) <-- error
    ...
):
    pass
```
## 如何在其他web框架使用?
目前只支持`starletter`和`flask`两个框架,如果要在其他框架中使用pait可以查照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.web.flask](https://github.com/so1n/pait/blob/master/pait/web/flask.py)
异步类型的web框架请参照 [pait.web.starletter](https://github.com/so1n/pait/blob/master/pait/web/starletter.py)
## IDE 支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`或得到IDE的支持,目前支持`Pycharm`和`Mypy`
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 完整示例
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
