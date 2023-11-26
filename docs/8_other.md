## 1.Implicit or explicit import
`pait` supports multiple web frameworks and if only one of them is installed in the project's dependency environment,
can use implicit import:
```Python3
from pait.app.any import pait, load_app, add_simple_route
```
But if multiple frameworks are installed at the same time, then the implicit import will throw an exception,
and it is recommended to use explicit import, as follows:
```Python3
from pait.app.flask import pait, load_app, add_simple_route
from pait.app.sanic import pait, load_app, add_simple_route
from pait.app.starlette import pait, load_app, add_simple_route
from pait.app.tornado import pait, load_app, add_simple_route
```
## 2.Internal Methods
`Pait` encapsulates a number of common methods.
Through these methods developers can quickly develop extension packages without considering compatibility with different web frameworks.
[OpenAPI routing](/3_2_openapi_route/) and [grpc-gateway](https://github.com/python-pai/grpc-gateway) are developed based on these methods.

### 2.1.data
`data` is the carrier for each `CoreModel`.
`Pait` decorates the route function to generate a `CoreModel` and store it in `pait.g.data` to support for configuration, documentation, etc feature.

### 2.2.load_app
The `CoreModel` stores a lot of information about the route functions, but the route functions are missing key OpenAPI information such as `url`, `method`, etc. So you need to use `load_app` to get more data before using OpenAPI.
So before using OpenAPI you need to use `load_app` to fill in the data, it's very simple to use, but you need to call it after registering all the routes, as follows.

!!! note
    [OpenAPI routing](/3_2_openapi_route/) automatically calls `load_app` before initialization

=== "Flask"

    ```Python3
    from flask import Flask

    from pait.app.flask import load_app

    app: Flask = Flask()

    load_app(app) # Wrong!!!
    # --------
    # app.add_url_rule
    # --------

    load_app(app) #  That's right
    app.run()
    ```

=== "Starlette"

    ```Python3
    import uvicorn
    from starlette.applications import Starlette

    from pait.app.starlette import load_app

    app: Starlette = Starlette()
    load_app(app) # Wrong!!!
    # --------
    # app.add_route
    # --------

    load_app(app) #  That's right
    uvicorn.run(app)
    ```

=== "Sanic"

    ```Python3
    from sanic import Sanic

    from pait.app.sanic import load_app

    app: Sanic = Sanic()
    load_app(app) # Wrong!!!

    # --------
    # app.add_route
    # --------

    load_app(app) #  That's right
    app.run()
    ```

=== "Tornado"

    ```Python3
    from tornado.web import Application
    from tornado.ioloop import IOLoop

    from pait.app.tornado import load_app

    app: Application = Application()
    load_app(app) # Wrong!!!
    # --------
    # app.add_handlers
    # --------
    load_app(app) #  That's right
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 2.3.HTTP exceptions
`Pait` provides an HTTP exception generator function for each web framework,
which generates HTTP standard exceptions for web frameworks by parameters such as HTTP status code, error content, Headers, etc.
They are used as follows.

=== "Flask"

    ```python
    from pait.app.flask import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Sanic"
    ```python
    from pait.app.sanic import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Starlette"
    ```python
    from pait.app.starlette import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Tornado"
    ```python
    from pait.app.tornado import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

In addition, `Pait` provides some HTTP exception responses as follows:
```python
from pait.app.any import pait
from pait.model import response

# response.Http400RespModel
# response.Http401RespModel
# response.Http403RespModel
# response.Http404RespModel
# response.Http405RespModel
# response.Http406RespModel
# response.Http407RespModel
# response.Http408RespModel
# response.Http429RespModel

@pait(response_model_list=[response.Http400RespModel])
def demo() -> None:
    pass
```
At the same time HTTP exception response Model also supports custom creation, the following example of use:
```python
from pait.model import response

# Create a response model with a status code of 500 and content-type as html
response.HttpStatusCodeBaseModel.clone(resp_model=response.HtmlResponseModel, status_code=500)
# Create a response model with status code 500 and content-type set to text
response.HttpStatusCodeBaseModel.clone(resp_model=response.TextResponseModel, status_code=500)
```

### 2.4.SimpleRoute
`Pait` unifies the route registration and response generation of different web frameworks through SimpleRoute.
Developers can easily create and register routes through SimpleRoute without considering compatibility.

!!! note
    Unified route response generation is provided by the `UnifiedResponsePluginProtocol` plugin.
    The `UnifiedResponsePluginProtocol` plugin is added to the route function when the route function is registered.

SimpleRoute is used as follows:

=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_simple_route_demo.py" hl_lines="8-20 24-32"

    --8<-- "docs_source_code/other/flask_with_simple_route_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_simple_route_demo.py" hl_lines="8-20 24-32"
    --8<-- "docs_source_code/other/starlette_with_simple_route_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_simple_route_demo.py" hl_lines="9-21 25-33"
    --8<-- "docs_source_code/other/sanic_with_simple_route_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_simple_route_demo.py" hl_lines="9-21 25-33"
    --8<-- "docs_source_code/other/tornado_with_simple_route_demo.py"
    ```
The first highlighted code creates three route functions according to the `SimpleRoute` standard, which is as follows:

- 1.The route functions need to be decorated by `pait`, and the `response_model_list` attribute cannot be empty (the response models of the route functions in the code are `JsonResponseModel`, `TextResponseModel`, `HtmlResponseModel`, these are all required by SimpleRoute, if there is no response model, then SimpleRoute can't register the route function to the web framework.)
- 2.The return value of the route function changes from a response object to a `Python` base type, and the returned `Python` base type needs to be consistent with the `response_data` of the response model.

The second highlight code is the registration of routes via the `add_simple_route` and `add_multi_simple_route` methods,
where `add_simple_route` can only register a single route and `add_multi_simple_route` can register multiple routes.
Both `add_simple_route` and `add_multi_simple_route` receive app and SimpleRoute instances,
whereas SimpleRoute supports only three attributes, as follows:

| Parameters | Description                                                |
|------------|------------------------------------------------------------|
| route      | A route function that conforms to the SimpleRoute standard |
| url        | The URL of the route                                       |
| method     | HTTP method of the route                                   |

In addition, `add_multi_simple_route` supports two optional parameters, as follows:

| Parameters | Description                                                                                                                                                                                      |
|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| prefix     | Route prefix, for example, if the prefix is "/api" and the url of SimpleRoute is "/user", the registered route URL is "/api/user".                                                               |
| title      | The title of the route group. For some frameworks, the route groups or blueprints they use need to be uniquely named, so the `title` should be different for different `add_multi_simple_route`s |


After running the code, test that the route works properly via the `curl` command:
<!-- termynal -->
```bash
>  curl http://127.0.0.1:8000/json
{}
>  curl http://127.0.0.1:8000/api/json
{}
>  curl http://127.0.0.1:8000/api/text
demo
>  curl http://127.0.0.1:8000/api/html
<h1>demo</h1>
```

### 2.5.Set and get web framework properties
`Pait` provides a unified method for setting and getting attribute values for Web frameworks, which are `set_app_attribute` and `get_app_attribute`.
The `set_app_attribute` and `get_app_attribute` can be used to set and get Web framework attributes at any time, as follows:

=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_attribute_demo.py" hl_lines="8 14"

    --8<-- "docs_source_code/other/flask_with_attribute_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_attribute_demo.py" hl_lines="10 16"
    --8<-- "docs_source_code/other/starlette_with_attribute_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_attribute_demo.py" hl_lines="8 14"
    --8<-- "docs_source_code/other/sanic_with_attribute_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_attribute_demo.py" hl_lines="10 16"
    --8<-- "docs_source_code/other/tornado_with_attribute_demo.py"
    ```

After running the code, test that the route works properly via the `curl` command:
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"status_code": 200}
```
As you can see by the result, the route function is able to get `client` and through `client` get the `status_code` of the url.


!!! note
    By setting property values for the web framework, can decouple the component from the framework and also make the component more flexible, but it is more recommended to use DI tools to realize decoupling, see [Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python).

## 3.How to use Pait with other web frameworks
Currently, `Pait` is still in the process of rapid iteration, so the main focus is on feature development.
If you want to use `Pait` in other frameworks that are not yet supported, or if you want to extend the functionality,
can refer to the two frameworks to make simple adaptations.

For synchronous web frameworks, please refer to [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask).

For asynchronous web framework, please refer to [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette).

## 4.Example code
See [example](https://github.com/so1n/pait/tree/master/example) for more complete examples.
## 5.Release
For detailed release info, please see [CHANGELOG](https://github.com/so1n/pait/blob/master/CHANGELOG.md)
