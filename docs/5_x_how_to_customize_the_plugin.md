
# How to customize the plugin
Both pre-plugin and post-plugin inherit from `PluginProtocol`, so they both implement the following methods:
```Python
from typing import Any, Dict

class PluginProtocol(object):

    def __post_init__(self, **kwargs: Any) -> None:
        pass

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        ...

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        ...

    @classmethod
    def build(cls, **kwargs: Any) -> "PluginManager[_PluginT]":
        ...

    def __call__(self, context: "PluginContext") -> Any:
        ...
```
If want to customize the plugin, need to inherit `PrePluginProtocol` or `PostPluginProtocol` depending on the plugin type and implement the methods mentioned above.
The methods in `PluginProtocol` correspond to the different lifecycles of the plugin, which are the build of the plugin - `build`, the pre-check of the plugin - `pre_check_hook`, the pre-load of the plugin - `pre_load_hook`, the initialization of the plugin - `__post_init__`, and the run of the plugin `__call__`.

## 1.Life cycle
### 1.1.Build of the plugin
The `build` method of a plugin actually stores the plugin and its corresponding required initialization parameters and is called by `Pait`.
If want to create a pre-plugin that uses the variables `a`, `b`, then the plugin's implementation code would look like this:
```python
from pait.plugin.base import PrePluginProtocol

class DemoPlugin(PrePluginProtocol):
    a: int
    b: str

    @classmethod
    def build(
        cls,
        a: int,
        b: str,
    ) -> "PluginManager[_PluginT]":
        cls.build(a=a, b=b)
```
First of all, `DemoPlugin` is defined to have `a` and `b` attributes and neither of them is assigned a value,
which means that the `DemoPlugin` plugin requires the `a` and `b` parameters, and the plugin fails to initialize if the `a` and `b` parameters are not passed through the `build` method.

### 1.2.Pre-check of plugins
Different plugins depend on different properties of `CoreModel` ,
and `pre_check_hook` checks whether the current `CoreModel` meets the plugin's requirements before the plugin is initialized,
to detect problems as early as possible.
The code is as follows:
```Python
from typing import Dict
from pait.plugin.base import PrePluginProtocol
from pait.model.status import PaitStatus

class DemoPlugin(PrePluginProtocol):
    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        if pait_core_model.status is not PaitStatus.test:
            raise ValueError("Only functions that are in test can be used")
        if not isinstance(kwargs.get("a", None), int):
            raise TypeError("param `a` type must int")
        super().pre_load_hook(pait_core_model, kwargs)
```
The sample code through the `pre_check_hook` for two checks, the first check is to determine whether the state of the current function is set to `TEST`,
the second check the type of the parameter `a` is whether the type of int, in the case of checking the failure of an exception will be thrown to interrupt the operation of the program.
### 1.3.Pre-load of plugins
Each route function decorated by `Pait` stores some initial values in `CoreModel`.
The plugin will extract the values from the `CoreModel` at runtime and process them, but it is time consuming to extract the data again for each request.
This can be done by extracting the data and saving it with `pre_load_hook` to reduce repetitive operations.
For example:
```Python
from typing import Dict
from pait.plugin.base import PrePluginProtocol
from pait.model.response import JsonResponseModel

class DemoPlugin(PrePluginProtocol):
    example_value: dict

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if not pait_core_model.response_model_list:
            raise ValueError("Not found response model")
        response_model = pait_core_model.response_model_list
        if not issubclass(response_model, JsonResponseModel):
            raise TypeError("Only support json response model")
        kwargs["example_value"] = response_model.get_example_value()
        return super().pre_load_hook(pait_core_model, kwargs)
```
The `DemoPlugin` is defined to require a parameter called `example_value`.
However, this parameter is not passed through the `build` method,
but is obtained by parsing the example value of the response model object in the `pre_load_hook` method.
which gets its example data via the `get_example_value` of the response object and stores it in the `example_value` of `kwargs`.
After that, `DemoPlugin` can store the `example_value` of `kwargs` to its own `example_value` property during the initialization phase.

### 1.4.`__post_init__`
As you know from the above methods, `kwargs` is a container that stores the plugin's initialization parameters,
which will be used by the `build`, `pre_check_hook`, and `pre_load_hook` methods.
It is then written to the plugin instance via the plugin's `__init__` method.

However, this process is handled automatically by `Pait` based on the properties of the plugin, which may not be compatible with some scenarios.
So the plugin executes the `__post_init__` method in the last step of initialization, and the developer can complete the custom plugin initialization logic with the `kwargs` variable in the `__post_init__` method.

### 1.5.`__call__`
`Pait` will organize the plugins in order and set the next plugin to the current plugin's `next_plugin` variable.
When a request hits, `Pait` passes the request data to the `__call__` method of the first plugin and waits for the plugin to process and return.
And each plugin will call the `self.next_plugin` method in the `__call__` method to continue calling the next plugin as follows.
```Python
from typing import Any
from pait.plugin.base import PrePluginProtocol


class DemoPlugin(PrePluginProtocol):
    def __call__(self, context: "PluginContext") -> Any:
        next_plugin_result = None
        try:
            next_plugin_result = self.next_plugin(context)
        except Exception as e:
            pass
        return next_plugin_result
```
In this sample code, plugin functionality can be implemented before or after calling `next_plugin` and catch `next_plugin` exceptions in the `except` syntax block.
Also, each plugin is driven by the previous plugin and plugins do not affect each other's functionality, but they can share data via `context`.

It is also possible to don't calling the `next_plugin` method to return a value or to throw an exception, as follows:
```Python
from typing import Any
from pait.plugin.base import PrePluginProtocol


class RaiseExcDemoPlugin(PrePluginProtocol):
    def __call__(self, context: "PluginContext") -> Any:
        raise RuntimeError("Not working")
```
When the plugin is executed, `Pait` does not call all subsequent plugins and route functions and throws an exception.


## 2.A real-world example
Here's a simple example of a implementation based on the `starlette` framework:
```py
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None)
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
The route function is provided with parameter validation by `Pait`,
when the caller's parameter does not match the validation rules,
the route function throws an exception and is caught by `starlette` and then distributed to the `api_exception` function to handle.
For example, a request that carries no request parameters:
<!-- termynal -->
```bash
>  ~ curl http://127.0.0.1:8000/api/demo
{"data":"Can not found uid value"}
```
Since `Pait` finds a missing parameter uid when validating the request parameters,
an error is thrown and caught by `api_exception` and an exception response is generated and returned to the caller.

Assuming that exceptions to the route function do not want to be handled by `api_exception`, a plugin can be implemented to handle exceptions to the route function, as follows:
```py linenums="1"
from typing import Any, Dict
from pait.plugin.base import PrePluginProtocol
from pydantic import ValidationError
from pait.exceptions import PaitBaseException
from starlette.responses import JSONResponse


class DemoExceptionPlugin(PrePluginProtocol):

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if pait_core_model.func.__name__ != "demo":
            raise RuntimeError(f"The {cls.__name__} is only used for demo func")

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return await self.next_plugin(args, kwargs)
        except (ValidationError, PaitBaseException) as e:
            return JSONResponse({"plugin exc info": str(e)})
```

As you can see there are several features of this plugin:.

- 1.The plugin inherits `PrePluginProtocol`, this is because of the need to catch exceptions thrown by `Pait`.
- 2.The plugin determines whether the current plugin is a `demo` function through the `pre_check_hook` method, and throws an exception if it is not.
- 3.Since the route function is `async def`, the `__call__` method of the plugin is also infected by `async` and needs to be `async def`.

After creating the plugin, can use it in the route function, for example:
```python
@pait(plugin_list=[DemoExceptionPlugin.build])
async def demo(...): pass
```
Next restart the program and run the same request, can see that the response has changed:
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"plugin exc info":"File \"/home/so1n/demo.py\", line 48, in demo.\nerror:Can not found uid value"}
```
