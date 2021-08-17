# Pait
Pait是一个可以用于python任何web框架的api工具(目前只支持`flask`,`starlette`, `sanic`, `tornado(实验性)`, 其他框架会在Pait稳定后得到支持).

Pait可以让Python Web框架拥有像参数类型检查, 类型转换的功能(依赖于Pydantic和inspect), 和提供文档输出等功能。

[Pait成型历史](http://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/)

> NOTE:
>
> mypy check 100%
>
> test coverage 95%+ (排除api_doc)
>
> python version >= 3.7 (支持延迟注释)
>
> 功能正在拓展中...文档可能不太完善
>
> 以下代码没有特别说明, 都默认以`starlette`框架为例.
> 文档输出功能没有测试用例, 功能还在完善中

# 功能
 - [x] 参数校验和自动转化(参数校验依赖于`Pydantic`)
 - [x] 参数关系依赖校验
 - [x] 自动生成openapi文件
 - [x] 支持swagger,redoc路由
 - [x] 返回mock响应
 - [x] TestClient支持, 支持响应结果校验
 - [ ] 支持更多类型的http请求(目前只支持RESTful api)
 - [ ] 结合faker提供更好的mock响应
 - [ ] 本地api文档管理

# 安装
```bash
pip install pait
```

## 1.类型转换和类型校验
### 1.1.在路由函数中使用使用pait
在使用`Pait`之前, 先看看普通的路由函数代码:
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
在使用pait后,路由函数代码可以改写为:
```Python3
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
从上面可以看出代码精炼了不少, 这一切都是`pait`装饰器在发挥了作用, 它通过函数签名发现了该如何获取值, 值的类型是什么, 值对应的key是什么, 通过组装后交由`Pydantic`进行校验和转换后再根据函数签名返回给路由函数对应的参数。

以上面的`uid`为例子, 可以把
```Python3
from pait.field import Body

uid: int = Body.i(description="user id", gt=10, lt=1000)
```
拆解为:
```
<key>: <type> = <request data>
```
其中key就是参数名, type为参数类型, request data为参数的其他说明, 如body就代表request body的数据, gt就是参数最小值, lt则是参数最大值。

这里只是一个简单的demo,由于我们编写的model可以复用,所以可以节省到大量的开发量,上面的参数只使用到一种写法,下面会介绍pait支持的两种写法以及用途.

### 1.2.pait支持的参数写法
pait为了方便用户使用,支持多种写法(主要是TypeHints的不同):
- TypeHints为PaitBaseModel时:

    该写法主要用于参数来源于多个`Field`, 并想复用model的情况.
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
- TypeHints 为Pydantic.BaseModel时:

    主要用于参数都是来源于同一个Field, 并想复用model的情况.
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

> 注: 直接使用Field.Body(), `mypy`会检查到类型不匹配, 这时候只要改为Field.Body.i()即可解决该问题.

```Python
from pait.app.starlette import pait
from pait.field import Body


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i(),
) -> None:
    pass
```

`Pait`在进行参数校验和转化时也支持其他的功能,都是通过`<request data>`的参数来提供支持的:
- default: 提供默认值的功能, 如果请求参数没有这个参数的值, 则默认使用该值
- alias: 由于在Python的变量中无法用`Content-Type`来命名,按照`Python`的命名习惯只能以`content_type`来命名,而`content_type`是没办法直接从header中获取到值的,所以可以设置alias为`Content-Type`,这样`Pait`就可以获取到位于Header中`Content-Type`的值并赋给`content_type`变量.
- raw_return: 当值为True时, `Pait`不会以参数名为key来获取数据, 而是直接把整个数据赋值给对应的参数.

使用例子如下:
```Python
from pait.app.starlette import pait
from pait.field import Body, Header


@pait()
async def demo_post(
    # get uid from request body data
    uid: int = Body.i(default=100),
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
.请注意, 如果需要创建自己的`Field`, 请继承`pait.field.BaseField`.

此外还有一个名为`Depends`的field, 他继承于`object`, 他提供依赖注入的功能, 他只支持一个类型为函数的参数, 而该函数的参数写法也跟路由函数是一样的,下面是Depends的一个使用例子,通过Depends,可以在各个函数复用获取token的功能:

```Python
from pait.app.starlette import pait
from pait.field import Body, Depends


def demo_depend(uid: str = Body.i(), password: str = Body.i()) -> str:
    # fake db
    token: str = db.get_token(uid, password)
    return token


@pait()
async def test_depend(token: str = Depends.i(demo_depend)) -> dict:
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
) -> None:
    pass
```
### 1.5.异常
#### 1.5.1异常处理
pait并不会为异常进行响应,而是把异常处理交给用户自己处理,正常情况下,pait只会抛出`pydantic`的异常和`PaitBaseException`异常,用户需要自己捕获异常并进行处理,如下所示:
```Python
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request

from pait.exceptions import PaitBaseException


async def api_exception(request: Request, exc: Exception) -> None:
    """
    自己处理异常的逻辑
    """
    if isinstance(exc, PaitBaseException):
        pass  # 执行pait异常的相关逻辑
    elif isinstance(exc, ValidationError):
        pass  # 执行pydantic异常的逻辑

APP = Starlette()
APP.add_exception_handler(PaitBaseException, api_exception)
APP.add_exception_handler(ValidationError, api_exception)
```

#### 1.5.2异常提示
如果用户错误的使用`pait`,如错误的使用参数写法类型, 那`Python`在执行函数时会报错,但报错信息只说明pait的哪个逻辑运行错误,这样子对于用户排查错误是十分困难的.所以pait对报错进行了处理并做出提示,告诉用户是哪个引用到pait的路由函数出错和出错位置以及出错的参数,如果用户使用类似于`Pycharm`的IDE,还可以点击路径跳转到对应的地方.`pait`抛错信息如下,可以看出在`gen_tip_exc`函数中抛出的`PaitBaseException`出现了错误的文件,错误所在函数,还有错误的参数名:
```Bash
  File "/home/so1n/github/pait/pait/param_handle.py", line 65, in gen_tip_exc
    )
PaitBaseException: 'File "/home/so1n/github/pait/example/starlette_example.py", line 29, in demo_post2  kwargs param:content_type: <class \'str\'> = Header(key=None, default=None) not found in Header({\'host\': \'127.0.0.1:8000\', \'user-agent\': \'curl/7.52.1\', \'accept\': \'*/*\', \'content-type\': \'application/json\', \'data_type\': \'msg\', \'content-length\': \'38\'}), try use Header(key={key name})'
```
如果你想查看更多消息,那可以把日志等级设置为debug,`pait`会输出如下的日志信息.
```Python3
DEBUG:root:
async def demo_post(
    ...
    content_type: <class 'str'> = Header(key=None, default=None) <-- error
    ...
):
    pass
```
## 2.文档

`pait`会自动捕获路由函数的请求参数和url,method等信息, 此外还支持标注一些相关信息, 这些标注只会在Python程序开始运行时加载到内存中, 不会对请求性能造成影响, 如下面的例子:

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
参数:
- author: 编写接口的作者列表
- group: 接口所属的组(该选项目前不会用于openapi)
- status: 接口的状态, 目前只支持PaitStatus的几种状态(该选项只有下线相关的才会用于openapi并标注为弃用)
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
- response_model_list: 返回的结果数据, 需要继承于`pait.model.PaitResponseModel`.由于`pait`是web框架的拓展,不会修改框架的代码, 所以该参数不会用于普通的请求判断(也不应该用于生产环境), 目前只会用于文档生成, mock响应生成, TestClient校验。


### 2.1.openapi
#### 2.1.1.openapi文档输出
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
from pait.app.starlette import load_app

# 提取路由信息到pait的数据模块
pair_dict = load_app(app)
# 根据数据模块的数据生成路由的openapi
PaitOpenApi(pair_dict)
```
#### 2.1.2.OpenApi路由
`Pait`目前支持openapi.json路由, 同时支持`Redoc`和`Swagger`的页面展示, 而这些只需要调用`add_doc_route`函数即可为`app`实例增加三个路由:
- /openapi.json
- /redoc
- /swagger
如果想定义前缀, 如定义为/doc/openapi.json, 则只要通过prefix参数把/doc传进去, 具体例子如下:
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


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)
# 把路由注入到app中
add_doc_route(app)
# 把路由注入到app中, 并且以/doc为前缀
add_doc_route(app, prefix='/doc')
```
### 2.2.其他文档输出
> 注: 功能正在完善中...

`pait`除了参数校验和转化外还提供输出api文档的功能, 通过简单的配置即可输出完善的文档.
注: 目前只支持输出md以及openapi格式的json和yaml. 关于md的输出见
[文档输出例子](https://github.com/so1n/pait/blob/master/example/api_doc/example_doc)

## 3.隐式引入和显示引入
`pait`对多个框架都提供支持, 如果一个项目中只安装了其中的一个框架, 那么可以使用隐式引入:
```Python3
from pait.app import add_doc_route, load_app, pait

```
但是如果同时安装了多个框架, 那么上面的引入会抛出错误, 建议使用显示引入, 如:
```Python3
from pait.app.starlette import add_doc_route, load_app, pait

```
## 4.config, data与load_app
- data
由于`pait`的通过一个装饰器来提供功能支持, 所以在编译器启动时, 所有数据都注入到data中, 为后续的文档生成等功能提供支。
- load_app
data里面有很多路由函数的信息, 但是会缺少关键的参数如`url`, `method`等。
所以还需要使用load_app把相关参数与`pait`装饰器装饰的路由函数数据在data中绑定, 使用方法很简单, 不过要记住, 一定要在注册所有路由后再调用:
  ```Python3
  from starlette.applications import Starlette

  from pait.app.starlette import load_app

  app: Starlette = Starlette()
  # 错误的
  load_app(app)
  # --------
  # app.add_route
  # --------

  # 成功的
  load_app(app)
  ```
- config
config能为`pait`提供一些配置支持, 它需要尽快的初始化, 最佳的初始化位置就是在app初始化之前进行初始化,  同时整个运行时只允许初始化一次
  ```Python
  from starlette.applications import Starlette

  from pait.app.starlette import load_app
  from pait.g import config

  config.init_config(author="so1n")
  app: Starlette = Starlette()
  # --------
  # app.add_route
  # --------
  load_app(app)
  ```

参数介绍:
- author: 全局的默认API作者, 如果`@pait`中没有填写author, 会默认调用到`config.author`
- status: 全局的默认API状态, 如果`@pait`中没有填写status, 会默认调用到`config.status`
- enable_mock_response: 决定这次运行是返回正常的响应还是根据`response_model`返回mock响应
- enable_mock_response_filter_fn: 默认支持多个`response_model`, mock响应默认只取第一个`response_model`, 如果觉得这个不符合自己想要的`response_model`, 则可以配置该函数来返回自己想要的结果
- block_http_method_set: 有一些web框架会自动帮忙把一些路由函数添加`HEAD`等请求方法, `pait`是无法识别哪些是框架添加, 哪些是用户自己添加的, 这时可以通过该参数屏蔽一些`method`
- default_response_model_list: 在设计一些API接口时, 通常有一些默认的异常响应, 只需要配置该参数即可应用到全局
- json_type_default_value_dict: 配置json类型的默认值
## 5.TestClientHelper
`pait`为每个框架都封装了一个对应的`TestCLientHelper`类, 通过该类可以更方便的编写测试用例, 同时还能对结果的数据结构跟`response_model`对比进行校验。
具体用法可以见[starlette例子](https://github.com/so1n/pait/blob/master/tests/test_app/test_starlette.py#L80)
参数说明:
  - client: 框架对应的test client
  - func: 对应被`pait`装饰的路由函数
  - pait_dict: `pait` meta data, 如果为空则内部会自动生成
  - body_dict: 请求的json数据
  - cookie_dict: 请求的cookie数据
  - file_dict: 请求的文件数据
  - form_dict: 请求的form数据
  - header_dict: 请求的header数据
  - path_dict: 请求的path数据
  - query_dict: 请求的query数据
## 6.如何在其他web框架使用?
如果要在其他尚未支持的框架中使用pait, 或者要对功能进行拓展, 可以查照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

## 7.IDE 支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`或得到IDE的支持,目前支持`Pycharm`和`Mypy`
- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)
- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 8````.完整示例
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
