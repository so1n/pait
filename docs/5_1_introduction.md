`Pait`的核心是一个装饰器，这个装饰器只做被装饰函数的处理和插件的初始化，真正负责功能实现的都是这些被装饰器初始化的插件，其中`Pait`的类型转换与参数校验功能是一个核心插件。

开发者可以通过`Pait`传入需要的装饰器，然后程序在启动的时候，会以拦截器的形式把插件按照顺序进行初始化，如果是前置形插件，那么它会被放置在类型转换与参数校验插件之前，否则就会放在后面。
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

首先请求会被中间件进行处理，然后再执行查找路由的功能，当找不到路由时就会返回`Not Found`的响应给客户端，如果找到了对应的路由，就会因为进入到了`Pait`的处理逻辑，首先会先进入到前置插件处理请求，
这时候前置插件只能得到框架对应的`request`参数(如果是`flask`框架，则没有)，前置插件处理完毕后就会进入到核心插件进行参数提取和校验转换功能，并把参数传递给后置插件，交由后置插件进行处理，
最后才经由后置插件把参数交给真正的路由函数处理生成响应。


在`Pait`中为了防止多个请求共享到了相同的插件变量，所以不支持直接引入插件，而是需要通过一个名为`PluginManager`的类来托管，如下代码：
```py hl_lines="14"
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.plugin import PluginManager
from pait.plugin.required import AsyncRequiredPlugin

from pait.app.starlette import pait
from pait import field


@pait(
    post_plugin_list=[PluginManager(AsyncRequiredPlugin, required_dict={"email": ["username"]})]
)
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None)
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
高亮部分通过`post_plugin_list`来引入一个后置插件`AsyncRequiredPlugin`，这个插件需要一个名为`required_dict`的参数，所以这里使用`PluginManager`来托管
`AsyncReuiredPlugin`插件，同时把对应的参数填入到`PluginManager`中，这样插件`AsyncReuiredPlugin`就可以在收到请求的时候生效了。
这个函数本意上参数`uid`为必填参数，而参数`user_name`和`email`是选填参数，但是通过`AsyncReuiredPlugin`插件后校验逻辑就发生了变化了，
当参数`username`不为空时，`email`也不能为空。
