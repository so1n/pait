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
@pait(
    post_plugin_list=[
        PluginManager(RequiredPlugin, required_dict={"email": ["username"]})
    ]
)
```
这段代码使用到的是一个名为`RequiredPlugin`的插件，这个插件属于后置形插件，所以是以`post_plugin_list`来传入插件。
同时`Pait`为了防止多个请求共享到相同的插件变量，所以不支持直接引入插件，而是需要通过一个名为`PluginManager`的类来托管，
其中，`RequiredPlugin`插件要求传入一个`required_dict`参数，需要把这个参数一并写入到`PluginManager`中，由`PluginManager`来初始化和运行插件。
