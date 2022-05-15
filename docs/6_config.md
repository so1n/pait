## config
config能为`Pait`提供一些配置支持, 不过由于`Pait`是以一个装饰器机制运行着，所以不是路由函数运行时来读取配置，而是`config`主动去覆盖路由函数对应的`Pait`属性，所以它有一个限制，就是需要在app被运行之前，`load_app`之后初始化, 同时整个运行时只允许初始化一次，如下代码：
```Python
from starlette.applications import Starlette
from pait.g import config
from pait.app import load_app

# ------
# 通过from ... import 导入路由模块
# ------

app: Starlette = Starlette()
# --------
# app.add_route
# --------
load_app(app)
config.init_config(author="so1n")
# --------
# run app
# --------
```
该代码中在`run app`代码块之前通过调用`config.init_config`进行初始化，目前`config.init_config`支持以下几个参数:

- author: 全局的默认API作者, 如果`@pait`中没有填写author, 则路由函数对应的auth为`config.author`
- status: 全局的默认API状态, 如果`@pait`中没有填写status, 则路由函数对应的status为`config.status`
- json_type_default_value_dict: 配置json类型的默认值，用于Pait生成一些默认Json值。
- python_type_default_valur_dict: 配置Python类型的默认值，用于Pait生成一些Python默认值。
- json_encoder: Pait全局调用的Json序列化的对象
- i18n_local: Pait全局使用的i18n语言
- i18n_config_dict: Pait i18n的字段配置，如果跟默认的配置有相同的Key则会覆盖掉对应Key的值
- apply_func_list: 按照一定规则适配路由函数属性的函数列表

## apply func介绍
在使用`Pait`的过程中可能会依据路由函数对应的生命周期来应用不同的`Pait`属性，比如对于`status`为design的路由函数，往往会使用Mock插件，而对于`status`为test的路由函数，往往会使用响应结果检查的插件等等。如果每次都是手动去改会非常麻烦，这时候就可以使用apply func功能。

`Pait`提供了一系列的apply func，每个apply func只有应用一种`Pait`属性，他们都是接收2个参数，第一个参数是路由函数`Pait`对应属性要要应用的值，第二个参数是匹配规则，匹配规则封装在一个`MatchRule`对象中，对象如下：
```Python
MatchKeyLiteral = Literal[
    "all",              # 所有路由函数都会匹配
    "status",           # 路由函数的status为对应值得都会匹配
    "group",            # 路由函数的group为对应值得都会匹配
    "tag",              # 路由函数的tag包含对应值得都会匹配
    "method_list",      # 路由函数的http请求方法包含对应值得都会匹配
    "path",             # 路由函数的url与输入的正则匹配到的都会匹配
    "!status",
    "!group",
    "!tag",
    "!method_list",
    "!path",
]


@dataclass
class MatchRule(object):
    key: MatchKeyLiteral = "all"
    target: Any = None
```
这个对象的Key是指路由函数`Pait`属性的Key，其中`all`代表所有路由函数都匹配，以`!`开头的代表是反向匹配，比如`MatchRule(!status, "test")`代表是匹配`status`的值不是`test`的路由函数，而target则是对应的值。

!!! note Note
    需要注意的是，apply func提供的是追加功能，并不会覆盖掉之前的值。

### apply_extra_openapi_model
在使用Web框架的时候，经常会使用中间件等其它用到请求参数的应用，比如有一个中间件，他会根据App版本号来进行限制，版本号小于1的都返回404。这种情况`Pait`无法托管到这个中间件使用的请求值，导致导出的OpanAPI文件，会缺少这个请求值，这时可以使用`apply_extra_openapi_model`来解决这个问题，它的使用方法如下：
```Python
from pait.field import Header
from pait.extra.config import apply_extra_openapi_model

class DemoModel(BaseModel):
    """中间件一般都是通过Header读取对应的版本号值"""
    version_code: int = Header.i(description="版本号")
    version_name: str = Header.i(description="版本名称")


# 通过apply_extra_openapi_model应用当前这个Model，由于中间件都是应用到所有的路由函数，所以直接使用MatchRule的默认值。
config.init_config(apply_func_list=[apply_extra_openapi_model(DemoModel)])
```
### apply_response_model
与apply_extra_openapi_model一样，在使用中间件限制版本号小于1的时候，可能返回的是一个内部的响应，这时候可以使用apply_response_model来添加一个默认的响应，需要注意点是，添加的这个默认响应模型的`is_core`属性必须为False，使用方法如下：
```Python
from pait.extra.config import apply_response_model
from pait.g import config
from pait.model.response import PaitHtmlResponseModel



class DefaultResponseModel(PaitHtmlResponseModel):
    is_core = False


# 由于中间件都是应用到所有的路由函数，所以直接使用MatchRule的默认值。
config.init_config(apply_func_list=[apply_response_model([DefaultResponseModel])])
```
### apply_block_http_method_set
由于`Pait`只是一个装饰器，他只能捕获到路由函数本身的属性，像Url, Http方法之类的需要后续调用`load_app`来补全，但是很多Web框架会自动为路由函数补上`HEAD`，`OPTIONS`等Http方法，即使开发者在注册路由时并没有填写，这样会导致导出来的OpenAPI数据会很多，这时可以使用`apply_block_http_method_set`来禁用一些方法不被`Pait`捕获，使用方法如下：
```Python
from pait.extra.config import apply_block_http_method_set
from pait.g import config


config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
```
### apply_default_pydantic_model_config
前面说到，`Pait`实际上会把开发者填写的函数签名转换为一个`pydantic.BaseModel`再进行校验和类型转换，这种情况下有时候需要使用`pydantic.BaseConfig`功能，比如`pydantic`默认情况下不会对开发者填写的`default`值进行校验，如果需要进行校验，则需要使用`pydantic.BaseConfig`功能，这时就可以使用`apply_default_pydantic_model_config`，使用方法如下：
```Python
from pait.extra.config import apply_default_pydantic_model_config
from pait.g import config
from pydantic import BaseConfig


class MyBaseConfig(BaseConfig):
    validate_assignment = True


config.init_config(apply_func_list=[apply_default_pydantic_model_config(MyBaseConfig)])
```
### apply_multi_plugin
插件是`Pait`的重要组成部分，其中有些插件只适用了接口的某些生命周期，所以比较推荐以下这样的写法，根据路由函数的状态来判断要应用哪些插件，如下:
```Python
from pait.app.starlette.plugin.mock_response import AsyncMockPlugin
from pait.app.starlette.plugin.check_json_resp import AsyncCheckJsonRespPlugin
from pait.extra.config import apply_multi_plugin
from pait.g import config
from pait.model.core import MatchRule
from pait.model.status import PaitStatus


config.init_config(
    apply_func_list=[
        apply_multi_plugin(
            # 为了能复用插件，这里只允许lambda写法，也可以使用pait自带的create_factory
            [lambda: AsyncMockPlugin.build()],
            # 限定status为design的使用Mock插件
            match_rule=MatchRule(key="status", target=PaitStatus.design)
        ),
        apply_multi_plugin(
            [lambda: AsyncCheckJsonRespPlugin.build()],
            # 限定status为test的使用响应体检查插件
            match_rule=MatchRule(key="status", target=PaitStatus.test)
        ),
    ]
)
```
### apply_pre_depend
大多数时候可能会为某一组路由函数使用一个token检验函数，这种情况不适合使用中间件，但是一个一个路由函数去添加depend却是很麻烦的一件事，这时可以使用`apply_pre_depend`,使用方法如下：
```Python
from pait.extra.config import apply_pre_depend
from pait.field import Header
from pait.g import config
from pait.model.core import MatchRule


def check_token(token: str = Header.i("")) -> bool:
    return bool(token)


config.init_config(
    apply_func_list=[
        # 匹配url以/api/v1/user开头的
        apply_pre_depend(check_token, match_rule=MatchRule(key="path", target="^/api/v1/user")),
        # 匹配路由函数的group属性为user的
        apply_pre_depend(check_token, match_rule=MatchRule(key="group", target="user"))
    ],
)
```
