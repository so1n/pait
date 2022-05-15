`Pait`的核心是一个装饰器，这个装饰器只做被装饰函数的处理和插件的初始化，真正负责功能实现的都是这些被装饰器初始化的插件，其中上面所述`Pait`的类型转换与参数校验功能是`Pait`的一个核心插件。

## 简单介绍
开发者可以通过`Pait`传入需要的插件，然后程序在启动的时候，会以拦截器的形式把插件按照顺序进行初始化，如果该插件是前置形插件，那么它会被放置在类型转换与参数校验插件之前，否则就会放在后面。
前置插件与后置插件除了他们自身的`is_pre_core`属性不同外，它们的最主要的区别是获得到的参数不同，前置插件获得的是Web框架传递过来的请求参数，可以把它当成一个简单版的中间件，而后置形插件读到的是`Pait`核心插件转换后的请求数据，以下面的函数为例子：
```Python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    uid: str = field.Query.i(),
    user_name: str = field.Query.i(),
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
假设代码中的`app`已经装载了一个中间件和对应的`Pait`插件，在收到一个请求时，它的处理逻辑会变为如下图:
![pait-plugin](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1647762511992pait-plugin.jpg)

当请求进来后会先由Web框架的中间件处理，然后Web框架会执行查找路由的功能，当找不到路由时就会返回`Not Found`的响应给客户端，如果找到了对应的路由，就会把请求传入到到`Pait`的处理逻辑。在`Pait`的处理逻辑中请求会先被前置插件处理，
这时候前置插件只能得到框架对应的`request`参数(如果是`flask`框架，则没有)，当前置插件处理完毕后就会把请求传入到核心插件进行参数提取和校验转换，经核心插件处理完后会把提取的参数传递给后置插件，交由后置插件进行处理，
最后才经由后置插件把参数交给真正的路由函数处理生成响应并一一返回。

## 如何使用
目前`Pait`提供`plugin_list`和`post_plugin_list`来供开发者传入前置插件和后置插件，如下：
```Python
from pait.plugin.required import RequiredPlugin

@pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["username"]})])
```
这段代码使用到的是一个名为`RequiredPlugin`的插件，这个插件属于后置形插件，所以是以`post_plugin_list`来传入插件。同时，由于插件是在收到请求的时候才会进行初始化，为了防止多个请求共享到相同的插件变量，`Pait`不支持直接初始化插件，而是使用`build`方法来使用插件(所以不为`__init__`方法提供准确的函数签名)。

如果考虑到插件的复用，推荐使用`create_factory`函数，该函数支持[PEP-612](https://peps.python.org/pep-0612/)，支持IDE提醒和类型检查，`create_factory`使用方法如下：
```Python
from pait.util import create_factory

# 首先传入插件的build方法，并把build需要的参数传进去
# 然后得到的是一个可调用的方法
required_plugin = create_factory(RequiredPlugin.build)(required_dict={"email": ["username"]})

# 直接调用create_factory的返回，这时候插件会注入到路由函数中并进行一些初始化，同时也不影响其它路由函数的使用
@pait(post_plugin_list=[required_plugin()])
def demo_1():
    pass

@pait(post_plugin_list=[required_plugin()])
def demo_2():
    pass
```

## 关闭预检查
`Pait`是一个装饰器，用来装饰路由函数，所以在程序启动的时候会直接运行，装填各种参数。不过在把插件装填到路由函数时会调用到插件的`pre_check`方法，对用户使用插件是否正确进行校验，比如下面的代码:
```Python
@pait()
def demo(
    uid: str = Body.i(default=None)
)
```
在启动的时候核心插件会校验到用户填写的`default`值并不属于`str`类型，所以会抛出错误。不过这类检查可能会影响到程序的启动时间，所以建议在测试环境下才通过`pre_check`进行检查，而在生产环境则关闭，而关闭的方法很简单，通过设置环境变量`PAIT_IGNORE_PRE_CHECK`为True即可关闭检查。
