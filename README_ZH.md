# Pait
Pait是一个可以用于python任何web框架的api工具(目前只支持`flask`,`starlette`, `sanic`, `tornado(实验性)`, 其他框架会在Pait稳定后得到支持).

Pait的核心功能是让你可以在任何Python Web框架拥有像FastAPI一样的类型检查和类型转换的功能(依赖于Pydantic和inspect), 以及提供文档输出功能。

Pait的文档输出功能愿景是代码既文档,只需要简单的配置,则可以得到一份md文档或者openapi(json, yaml)

[了解如何实现类型转换和检查功能](http://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)

> mypy check 100%
> 
> test coverage 95%+ (排除api_doc)
> 
> python version >= 3.7 (支持延迟注释)
# 安装
```bash
pip install pait
```

# 使用
注:以下代码没有特别说明, 都默认使用`starlette`框架.
注:文档输出功能没有测试用例, 功能还在完善中 

## 1.类型转换和类型校验
### 1.1.在路由函数中使用使用pait
先看看普通的路由函数代码:
```Python
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def demo_post(request: Request) -> JSONResponse:
    body_dict: dict = await request.json()
    uid: int = body_dict.get('uid')
    user_name: str = body_dict.get('user_name')
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
在使用pait后,路由函数代码可以改为:

```Python
import uvicorn
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


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
```
可以看出,只需要对路由函数添加一个`pait`装饰器,并把`demo_post`的参数改为`model: PydanticModel = Body()`即可.
`pait`装饰器会解析参数, 通过`Body`知道需要获取post请求body的数据,并根据`conint(gt=10, lt=1000)`对数据进行转换和限制,并赋值给`PydanticModel`,用户只需要像使用`Pydantic`一样调用`model`即可获取到数据.

这里只是一个简单的demo,由于我们编写的model可以复用,所以可以节省到大量的开发量,上面的参数只使用到一种写法,下面会介绍pait支持的两种写法以及用途.

### 1.2.pait支持的参数写法
pait为了方便用户使用,支持多种写法(主要是TypeHints的不同):
- TypeHints 为PaitBaseModel时, 主要用于参数来源于多个`Field`, 并想复用model:
  
    PaitBaseModel只可用于args参数, 他是最灵活的, PaitBaseModel拥有大部分Pydantic.BaseModel的功能, 他的特点是当属性的值为Field类型时可以被Pait识别, 所以一个PaitBaseModel可以填写多个Field,这是Pydantic.BaseModel没办法做到的,使用示例:
    ```Python
    from pait.app.starlette import pait
    from pait.field import Body, Header
    from pait.model import PaitBaseModel


    class TestModel(PaitBaseModel):
        uid: int = Body()
        content_type: str = Header(default='Content-Type')


    @pait()
    async def test(model: PaitBaseModel):
        return {'result': model.dict()}
    ```
- TypeHints 为Pydantic.BaseModel时, 主要用于参数都是来源于同一个Field, 并想复用model: 
  
    Pydantic.BaseModel只可用于kwargs参数,且参数的type hints必须是一个继承于`pydantic.BaseModel`的类,使用示例:
    ````Python
    from pydantic import BaseModel

    from pait.app.starlette import pait
    from pait.field import Body
    
    
    class TestModel(BaseModel):
        uid: int
        user_name: str
    
    
    @pait()
    async def test(model: BaseModel = Body.i()):
        return {'result': model.dict()}
    ````
- TypeHints不是上述两种情况时:
  
    只可用于kwargs参数,且type hints并非上述两种情况, 如果该值很少被复用,或者不想创建Model时,可以考虑这种方式
    ```Python
    from pait.app.starlette import pait
    from pait.field import Body


    @pait()
    async def test(uid: int = Body.i(), user_name: str = Body.i()):
        return {'result': {'uid': uid, 'user_name': user_name}}
    ```
### 1.3.Field介绍
Field的作用是助于Pait从请求中获取对应的数据,在介绍Field的功能之前先看下面的例子:

与上面一样,`pait` 会根据Field.Body获取到请求的body数据,并以参数名为key获取到值,最后进行参数验证并赋值到uid.

```Python
from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i(),
):
    pass
```
下面的例子会用到一个叫default的参数.
由于在Python的变量中无法用Content-Type来命名,按照python的命名习惯只能以content_type来命名,而content_type是没办法直接从header中获取到值的,所以可以设置alias为Content-Type,这样Pait就可以获取到位于Header中Content-Type的值并赋给content_type变量.
还有一个例子用到了`raw_return`,并设置为True, 这时`Pait`不会以参数名`header_dict`为key来获取数据, 而是直接把整个header的数据赋值给header_dict.

```Python
from pait.app.starlette import pait
from pait.field import Body, Header


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i(),
    # get Content-Type from header
    content_type: str = Header.i(alias='Content-Type'),
    header_dict: str = Header.i(raw_return=True)
):
    pass
```
上面只演示了field中的Body和Header, 除此之外还有其他的field:
- Field.Body   获取到当前请求的json数据
- Field.Cookie 获取到当前请求的cookie数据
- Field.File   获取到当前请求的file数据,会根据不同的web框架返回不同的file对象类型
- Field.Form   获取当前请求的表单数据, 如果有多个重复的key, 只会返回第一个
- Field.Header 获取当前请求的header数据
- Field.Path   获取当前请求的path数据(如/api/{version}/test, 可以获得到version数据)
- Field.Query  获取到当前请求的url参数以及对应数据, 如果有多个重复的key, 只返回第一个
- Field.MultiQuery 获取当前请求的url参数数据, 返回key对应的列表
- Field.MultiForm 获取当前请求的表单数据, 返回key对应的列表

上面的所有field继承于`pydantic.fields.FieldInfo`,这里的大多数参数都是为了api文档而服务的,具体用法可以见[pydantic文档](https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation)
.请注意, 如果需要创建自己的Field, 请继承Field.BaseField.

此外还有一个名为Depends的field, 他继承于`object`, 他提供依赖注入的功能, 他只支持一个类型为函数的参数, 而该函数的参数写法也跟路由函数是一样的,下面是Depends的一个使用例子,通过Depends,可以在各个函数复用获取token的功能:

```Python
from pait.app.starlette import pait
from pait.field import Body, Depends


def demo_depend(uid: str = Body.i(), password: str = Body.i()) -> str:
    # fake db
    token: str = db.get_token(uid, password)
    return token


@pait()
async def test_depend(token: str = Depends.i(demo_depend)):
    return {'token': token}
```

### 1.4.requests对象
使用`Pait`后,使用request对象的次数占比会下降, 所以`Pait`并不返回request对象,如果你需要requests对象,那可以填写像`request: Request`一样的参数(需要使用TypeHints格式),即可得到web框架对应的requests对象

```Python
from starlette.requests import Request

from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
        request: Request,
        # get uid from request body data
        uid: int = Body.i()
):
    pass
```
### 1.5.异常
#### 1.5.1异常处理
pait并不会为异常进行响应,而是把异常处理交给用户自己处理,正常情况下,pait只会抛出`pydantic`的异常和`PaitBaseException`异常,用户需要自己捕获异常并进行处理,如下所示:
```Python
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from pait.exceptions import PaitBaseException


async def api_exception(request: Request, exc: Exception) -> Response:
    """
    自己处理异常的逻辑    
    """
    if isinstance(exc, PaitBaseException):
        pass  # 执行pait异常的相关逻辑
    else:
        pass

APP = Starlette()
APP.add_exception_handler(PaitBaseException, api_exception)
APP.add_exception_handler(ValidationError, api_exception)
```

#### 1.5.2异常提示
如果用户错误的使用pait,如错误的使用参数写法类型, 那Python在执行函数时会报错,但报错信息只说明pait的哪个逻辑运行错误,这样子对于用户排查错误是十分困难的.所以pait对报错进行了处理并做出如下提示,告诉用户是哪个引用到pait的路由函数出错和出错位置以及出错的参数,如果用户使用类似于`Pycharm`的IDE,还可以点击路径跳转到对应的地方.`pait`抛错信息如下,可以看出在`raise_and_tip`函数中抛出的`PaitBaseException`出现了错误的文件,错误所在函数,还有错误的参数名:
```Bash
  File "/home/so1n/github/pait/pait/param_handle.py", line 65, in raise_and_tip
    )
PaitBaseException: 'File "/home/so1n/github/pait/example/starlette_example.py", line 29, in demo_post2  kwargs param:content_type: <class \'str\'> = Header(key=None, default=None) not found in Header({\'host\': \'127.0.0.1:8000\', \'user-agent\': \'curl/7.52.1\', \'accept\': \'*/*\', \'content-type\': \'application/json\', \'data_type\': \'msg\', \'content-length\': \'38\'}), try use Header(key={key name})'
```
如果你想查看更多消息,那可以把日志等级设置为debug,pait会输出如下的日志信息.
```Python
DEBUG:root:
async def demo_post(
    ...
    content_type: <class 'str'> = Header(key=None, default=None) <-- error
    ...
):
    pass
```
## 2.文档输出
> 注: 功能正在完善中...

`pait`除了参数校验和转化外还提供输出api文档的功能, 通过简单的配置即可输出完善的文档.
注: 目前只支持输出md, json, yaml以及openapi格式的json和yaml. 关于md, json, yaml的输出见
[文档输出例子](https://github.com/so1n/pait/blob/master/example/api_doc/example_doc)

`pait`会自动捕获路由函数的请求参数和url,method等信息, 此外还支持标注一些相关信息, 这些标注只会在Python程序开始运行时加载到内存中, 不会对请求性能造成影响, 如下面的例子:
```Python
from example.param_verify.model import FailRespModel, UserSuccessRespModel
from pait.app.starlette import pait
from pait.model import PaitStatus


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
参数:
- author: 编写接口的作者列表
- group: 接口所属的组
- status: 接口的状态, 目前只支持PaitStatus的几种状态
  - 默认状态:
    - undefined: 未定义, 默认状态
  - 开发中:  
    - design: 设计中
    - dev: 开发测试中 
  - 开发完成:  
    - integration: 联调
    - complete: 开发完成 
    - test: 测试中
  - 上线:  
    - release: 上线
  - 下线:  
    - abnormal: 出现异常, 下线
    - maintenance: 维护中
    - archive: 归档
    - abandoned: 遗弃
- tag: 接口的标签
- response_model_list: 返回的结果数据, 需要继承于`pait.model.PaitResponseModel`


### 2.1.openapi
目前pait支持openapi的大多数功能,少数未实现的功能将通过迭代逐步完善

pait的openapi模块支持一下参数(下一个版本会提供更多的参数):
- title: openapi的title 
- open_api_info: openapi info的参数 
- open_api_tag_list: open api tag的相关描述 
- open_api_server_list: open api server 列表 
- type_: 输出的类型, 可选json和yaml 
- filename: 输出文件名, 如果为空则输出到终端

以下是openapi文档输出的示例代码(通过1.1代码改造).具体的见
[示例代码](https://github.com/so1n/pait/tree/master/example/api_doc)
以及
[文档输出例子](https://github.com/so1n/pait/blob/master/example/api_doc/example_doc)
```Python
import uvicorn
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


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

# 上面是跟1.1的例子一样

from pait.api_doc.open_api import PaitOpenApi
from pait.app import load_app

# 提取路由信息到pait的数据模块
pair_dict = load_app(app)
# 根据数据模块的数据生成路由的openapi
PaitOpenApi(pair_dict)
```

## 3.如何在其他web框架使用?
如果要在其他尚未支持的框架中使用pait, 或者要对功能进行拓展, 可以查照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

## 4.IDE 支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`或得到IDE的支持,目前支持`Pycharm`和`Mypy`
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 5.完整示例
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
