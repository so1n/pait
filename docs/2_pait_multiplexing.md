在上面的章节中，通过直接使用`Pait`装饰器来使用`Pait`的参数转换与类型校验功能，也有简单的说明通过`pre_depend_list`参数来使用`Pait`的Pre-Depend功能，
而在后面的章节中（特别是文档章节）会介绍`Pait`的其它功能，这些功能用需要通过指定的参数来启用，但是很多接口本身都有一些共性从而它们在使用`Pait`时填写的参数的一样的，
比如当一个开发者编写了几个接口时，可能会这样写:
```Python
from starlette.responses import Response
from pait.app.starlette import pait
from pait.model.status import PaitStatus

@pait(status=PaitStatus.test)
async def demo() -> Response:
    pass


@pait(status=PaitStatus.test)
async def demo1() -> Response:
    pass

@pait(status=PaitStatus.test)
async def demo2() -> Response:
    pass
```
这个示例代码共有3个接口，但是它们都使用相同的`Pait`的`status`参数，代表现在的接口都在测试中，
但是在后面上线的时候所有接口的状态都需要一个个的改为`release`，这是非常的麻烦，这时可以通过自己来实例化一个不同的`Pait`，达到复用的目的。


## 使用自己定制的Pait
在上面的使用中，我们都是通过:
```Python
from pait.app.starlette import pait
```
来引入一个`Pait`装饰器，这是一个最方便的使用方法，不过它本身是`Pait`类的单例，在考虑使用`Pait`的复用时，则需要通过`Pait`类入手，
来重新实例化一个自己定制的`Pait`，然后把接口的`Pait`替换为自己定义的`Pait`，比如下面的示例：
```py hl_lines="6 8 13 18"
from starlette.responses import Response
from pait.app.starlette import Pait
from pait.model.status import PaitStatus


global_pait: Pait = Pait(status=PaitStatus.test)

@global_pait()
async def demo() -> Response:
    pass


@global_pait()
async def demo1() -> Response:
    pass


@global_pait()
async def demo2() -> Response:
    pass
```
代码中创建一个变量名为`global_pait`的`Pait`，
它的`status`被指定为`PaitStatus.test`，然后把`global_pait`都应用到所有的接口函数中，这样的所有接口函数就等于前面应用的：
```Python
@pait(status=PaitStatus.test)
async def demo() -> Response:
    pass
```
如果在后续的代码迭代且接口函数需要集中变动时，我们只需要直接修改定义的`global_pait`的属性则可以让所有接口的`Pait`属性都得到更改。

## 创建子Pait
`Pait`可以通过`create_sub_pait`方法创建自己的子`Pait`，每个子`Pait`的属性都是继承于自己的父`Pait`属性，比如下面这段示例代码：
```Python
from pait.app.starlette import Pait

from pait.model.status import PaitStatus

global_pait: Pait = Pait(status=PaitStatus.test)
other_pait: Pait = global_pait.create_sub_pait()
```
`global_pait`是一个父`Pait`，而`other_pait`则是被`global_pait`创建的，此时它的`status`属性也跟`global_pait`的`status`属性一样都是`PaitStatus.test`。
但是也可以在创建的时候通过指定不同的值，使子`Pait`的属性被指定的值覆盖，比如这段代码:
```Python
from pait.app.starlette import Pait

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")
```
代码中`global_pait`与`user_pait`的`author`属性都是`("so1n", )`，但是`global_pait`的`group`属性为`global`，而`user_pait`的`group`属性为`user`。

子`Pait`创建之后就可以跟之前一样在接口函数使用了，比如下面的代码，用户登录接口函数`user_login`以及用户注销函数`user_logout`都使用`user_pait`，
他们共同拥有`group`为`user`的属性；而获取服务器时间戳的接口函数`get_server_timestamp`则单独使用的是`global_pait`，它的`group`为`global`。
```Python
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()
async def user_login() -> JSONResponse:
    pass

@user_pait()
async def user_logout() -> JSONResponse:
    pass

@global_pait()
async def get_server_timestamp() -> JSONResponse:
    pass
```
如果你突然想更改`user_logout`接口函数的`Pait`属性， 还可以在`user_logout`的`user_pait`装饰器填写对应的参数来达到更改的目的，
如下面的代码，其中高亮部分会把接口函数`user_logout`的`group`属性变为`user-logout`而不是`user`:
```py hl_lines="12"
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()
async def user_login() -> JSONResponse:
    pass

@user_pait(group="user-logout")
async def user_logout() -> JSONResponse:
    pass

@global_pait()
async def get_server_timestamp() -> JSONResponse:
    pass
```
