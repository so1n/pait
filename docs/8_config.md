config provide some functional configurations for `Pait`,
however, it is only allowed to be initialized once during the entire runtime of the program,
and it is recommended to do so after all routes have been added and `load_app` has been called,
as in the following code, `config.init_config` is called before the `run app` code block:
```Python
from starlette.applications import Starlette
from pait.g import config
from pait.app.any import load_app

# ------
# By `from ... import` import routing module
# ------

app: Starlette = Starlette()
# --------
# app.add_route
# --------
load_app(app)
config.init_config(author=("so1n", ))
# --------
# run app
# --------
```


`config.init_config` supports the following parameters:

| Parameters                     | Description                                                                                                                         |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| author                         | Global author of the default route function, if author in `@pait` is null, the author for the route function is `config.author`     |
| status                         | Global status of the default route function, if status in `@pait` is null, the status for the route function is  is `config.status` |
| json_type_default_value_dict   | Configure the default value of the json type, which will be useful when auto-generating the response.                               |
| python_type_default_value_dict | Configure a default value for the python type that will work when auto-generating the response.                                     |
| json_encoder                   | Pait's Json encoder  object                                                                                                         |
| apply_func_list                | A list of functions that change the attributes of the route function according to certain rules                                   |

## 1.apply func

When using `Pait`, it may be possible to use different `Pait` attributes depending on the route function lifecycle.
For example, if the `status` is `design`, the Mock plugin will be used, and if the `status` is `test`, the response check plugin will be used.
If you have to change the configuration manually every time, it will be very troublesome, and you can use the apply func function at this time.

!!! note
    This function can be thought of as a routing group, but don't think of it as middleware, as it can't handle routes that aren't decorated by `Pait`.

`Pait` provides a series of apply func, each apply func will only handle one kind of `Pait` attribute, its function protocol is as follows:
```python
from typing import Any, Optional
from pait.model.config import APPLY_FN
from pait.extra.config import MatchRule

def apply_func_demo(
    value: Any, match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    pass
```
It requires 2 parameters,
the first parameter is the value to be applied and the second parameter is to match which route functions need to be applied.

The `match_rule` parameter is an object called `MatchRule`,
which is initialized to accept two parameters,
one named `key` and the other named `target`.
Where `key` is the Key of the corresponding `Pait` attribute of the route function,
with a default value of `all` (which means that all route functions match).
Target is the value of the attribute to be matched, Key currently supports the following values:
```Python
MatchKeyLiteral = Literal[
    "all",              # Match all route functions
    "status",           # The status of the route function will be matched if it corresponds to the value
    "group",            # The group of the route function will be matched to the corresponding value
    "tag",              # The tag of the route function will match the corresponding values
    "method_list",      # The HTTP method of the route function will match the corresponding value
    "path",             # The URL of the route function matches the regular match of the input
    "!status",
    "!group",
    "!tag",
    "!method_list",
    "!path",
]
```
They are of three types.
The first type is `all`, such as  `MatchRule("all")` means that all route functions will match.
The second type is `status`, `group`, `tag`, `method_list`, `path`, such as `MatchRule("group", "demo")` means that route functions with a `group` of `demo` will be matched.
The last type starts with `! `, which means reverse matching, such as `MatchRule("!status", "test")` means that route functions that match `status` with a value other than `test` will be matched.

In addition to this, the matching rules support multi-rule matching for `&` and `|` as follows:
```Python
from pait.extra.config import MatchRule
from pait.model.status import PaitStatus

# Match the route function whose status is test or dev
MatchRule("status", PaitStatus.test) | MatchRule("status", PaitStatus.dev)
# Match the route function whose path is /api/user, method_list is GET, or group is gRPC
MatchRule("path", "/api/user") & (MatchRule("method_list", "GET") | MatchRule("group", "gRPC"))
```

!!! note Note
    It is important to note that `apply func` only appends the value for array-type values, not overrides the value.

### 1.1.apply_extra_openapi_model
When using the Web framework, may use some request parameters through the middleware,
these parameters will not be used in the route function.
For example, there is a middleware that gets the APP version from the Header,
and returns a 404 response for APP versions less than 1, and only allows access if the APP version is greater than 1.
In this case, `Pait` will not be able to get the request values used by the middleware,
resulting in the generated OpanAPI data missing these request values.
This can be solved by using `apply_extra_openapi_model`, which is used as follows:
```Python
from pydantic import BaseModel
from pait.field import Header
from pait.extra.config import apply_extra_openapi_model
from pait.g import config

class DemoModel(BaseModel):
    """Middleware generally reads the corresponding version value through the header"""
    version_code: int = Header.i(description="Version code")
    version_name: str = Header.i(description="Version name")


# Use the `apply_extra_openapi_model` to apply the current model,
# and use the default value of the MatchRule because the middleware is applied to all route functions.
config.init_config(apply_func_list=[apply_extra_openapi_model(DemoModel)])
```
### 1.2.apply_response_model
As with the `apply_extra_openapi_model`,
an exception response may be returned when using a middleware restriction with a version number less than 1.
In this case a default response can be added using apply_response_model, used as follows:
```Python
from pait.extra.config import apply_response_model
from pait.g import config
from pait.model.response import HtmlResponseModel



class DefaultResponseModel(HtmlResponseModel):
    response_data: str = "<h1> Default Html</h1>"


# Since middleware is applied to all route functions, the matching rules use the default values
config.init_config(apply_func_list=[apply_response_model([DefaultResponseModel])])
```
### 1.3.apply_block_http_method_set
`Pait` is a decorator, so it can only capture the attributes of the route function,
like URL, HTTP method parameters need to be added by `load_app`.
However, many web frameworks will automatically supplement the route function with HTTP methods like `HEAD`, `OPTIONS`, etc.
when registering the route function.
This will cause the OpenAPI data of the route function to contain HTTP methods such as `HEAD` and `OPTIONS`.
In this case, can use `apply_block_http_method_set` to disable some HTTP methods from being captured by `Pait`,
using the following method:
```Python
from pait.extra.config import apply_block_http_method_set
from pait.g import config


config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
```

### 1.4.apply_multi_plugin
Plugins are an important part of `Pait`, however there are plugins that only work for route functions with certain statuses.
It is recommended to use different plugins based on the `status` of the route function via `apply_multi_plugin` as follows:
```Python
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin
from pait.extra.config import apply_multi_plugin, MatchRule
from pait.g import config
from pait.model.status import PaitStatus


config.init_config(
    apply_func_list=[
        apply_multi_plugin(
            # In order to be able to reuse the plugin, the lambda writing method is used here,
            # and can also use the create_factory that comes with pait
            [lambda: MockPlugin.build()],
            # Using the Mock plugin for route functions where status is design
            match_rule=MatchRule(key="status", target=PaitStatus.design)
        ),
        apply_multi_plugin(
            [lambda: CheckJsonRespPlugin.build()],
            # Using the CheckJsonPlugin for route functions where status is test
            match_rule=MatchRule(key="status", target=PaitStatus.test)
        ),
    ]
)
```
### 1.5.apply_pre_depend
Most of the time, may use a Token check function for a group of route functions,
which is not suitable for middleware, but adding `depend` one by one to a route function is cumbersome,
so can use `apply_pre_depend`, which is used as follows:
```Python
from pait.extra.config import apply_pre_depend, MatchRule
from pait.field import Header
from pait.g import config


def check_token(token: str = Header.i("")) -> bool:
    return bool(token)


config.init_config(
    apply_func_list=[
        # Match url starting with /api/v1/user
        apply_pre_depend(check_token, match_rule=MatchRule(key="path", target="^/api/v1/user")),
        # Match route functions whose group attribute is user
        apply_pre_depend(check_token, match_rule=MatchRule(key="group", target="user"))
    ],
)
```
