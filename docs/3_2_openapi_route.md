`Pait` in addition to supporting the generation of OpenAPI content,
but also supports OpenAPI route generation.
by default, will provide `openapi.json` and some doc-ui route, such as the [document home](/index) sample code.
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo.py"

    --8<-- "docs_source_code/introduction/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo.py"
    --8<-- "docs_source_code/introduction/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo.py"
    --8<-- "docs_source_code/introduction/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo.py"
    --8<-- "docs_source_code/introduction/tornado_demo.py"
    ```
Through the sample code can be seen, just simply call `AddDocRoute` can be `app` bound OpenAPI route,
the specific route url and the corresponding function is shown in the table below:

| route url     | description                                                                                     | features                                                    |
|---------------|-------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| /openapi.json | Get OpenAPI's json response                                                                     |                                                             |
| /elements     | Use [elements](https://github.com/stoplightio/elements) to display document data                | UI is nice and simple, support request in page              |
| /redoc        | Use [Redoc](https://github.com/Redocly/redoc) to display  document data                         | UI is nice and simple, but does not support request in page |
| /swagger      | Use [Swagger](https://github.com/swagger-api/swagger-ui) to display document data               | Generic OpenAPI display UI, full-featured                   |
| /rapidoc      | Use [RapiDoc](https://github.com/rapi-doc/RapiDoc) to display document data                     | Fully featured; modernized UI; supports customized UI       |
| /rapipdf      | Provides a page where can download [RapiDoc](https://github.com/rapi-doc/RapiDoc) pdf documents | Poor support for non-English                                |

## 1.Use of OpenAPI routing
`AddDocRoute` can easily bind OpenAPI routes to `app` instances,
and `AddDocRoute` provides some parameters for developers to customize route extensions and to solve the complexity of production environments.
Currently `AddDocRoute` provides the following parameters:

| Parameters                 | Description                                                                                                                                                 |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| scheme                     | HTTP Schema, such as http or https                                                                                                                          |
| openapi_json_url_only_path | Generated openapi.json url that owns the path portion (scheme fails when this parameter is in effect)                                                       |
| prefix                     | A prefix for routing URLs                                                                                                                                   |
| pin_code                   | A simple security checksum                                                                                                                                  |
| title                      | Defines the title of the OpenAPI route. Note that when calling `AddDocRoute` multiple times to bind different OpenAPI routes, their titles should different |
| doc_fn_dict                | Implementation of UI pages in OpenAPI routes                                                                                                                |
| openapi                    | `Pait`'s OpenAPI class                                                                                                                                      |
| pait                       | `Pait` instances, OpenAPI will create child `pait` based on the this `pait` and use them. See [how to use Pait](/2_how_to_use_pait)                         |
| add_multi_simple_route     | Methods for binding routes to app instances, see [SimpleRoute](/8_other/#24simpleroute) section for details                                                                        |
| not_found_exc              | pin_code error exception                                                                                                                                    |

### 1.1.scheme
The HTTP Schema of OpenAPI routing can be explicitly specified through the scheme parameter, such as HTTP and HTTPS.

It is important to note that the HTTP Schema does not refer to the HTTP Schema used by the current service,
but rather the HTTP Schema used by the visitor.
For example, the current service specifies HTTP Schema, but in order to enhance the security of the service,
Add a layer of proxy in front of the service to support HTTPS, such as using Nginx.
In this case, the user can only access the service via `https://127.0.0.1/openapi.json`.
In order for the OpenAPI route to respond properly, should use `scheme="https"` when binding the OpenAPI route.

The example code is as follows:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, scheme="http")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, scheme="http")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, scheme="http")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, scheme="http")
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 1.2.openapi_json_url_only_path
When openapi_json_url_only_path is `False` by default, the generated OpenAPI Json url is complete (`http://example.com/openapi.json`).
When openapi_json_url_only_path is `True`, the generated OpenAPI Json url is `/openapi.json`.

!!! note
    - 1.The current OpenAPI UIs all support `/openapi.json`, but there is no guarantee that subsequent OpenAPI UIs will support them.
    - 2.When using `openapi_json_url_only_path`, the `schema` parameter will be invalidated.

The example code is as follows:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, openapi_json_url_only_path=True)
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    app.listen(8000)
    IOLoop.instance().start()
    ```
### 1.3.prefix
By default, `AddDocRoute` will bind the route to the app instance according to the following URL:

- /openapi.json
- /redoc
- /swagger
- /rapidoc
- /rapipdf
- /elements


However,
using the default `/` prefix is not a good behavior,
and it is recommended to specify a URL prefix that matches your own habits via `prefix` when using it.
For example `/api-doc`, then `AddDocRoute` will bind to the route with the following URL:

- /api-doc/openapi.json
- /api-doc/redoc
- /api-doc/swagger
- /api-doc/rapidoc
- /api-doc/rapipdf
- /api-doc/elements

The example code is as follows:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, prefix="/api-doc")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    app.listen(8000)
    IOLoop.instance().start()
    ```
### 1.4.pin_code
`pin_code` provides a simple security mechanism to prevent outsiders from accessing OpenAPI routes, which is used as follows:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, pin_code="6666")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    app.listen(8000)
    IOLoop.instance().start()
    ```
After run the code,
If you visit `http://127.0.0.1:8000/swagger` in your browser, you will not find the corresponding page,
but if you visit `http://127.0.0.1:8000/swagger/pin_code=6666` instead, the page will be displayed normally.

!!! note
    - 1.Normally OpenAPI routes should not be exposed for external use.
        Security needs to be enhanced by tools such as Nginx (e.g., IP whitelisting restrictions),
        and the security of this mechanism is much higher than that of `pin_code`.
    - 2.Customized security checks can be added to OpenAPI via `Pait`'s Pre-depend.
    - 3.If the pin code checksum carried by the access fails, a 404 exception will be returned by default,
        which can be customized via `not_found_exc`.


### 1.5.Title

Title has two feature, one is used to define the Title attribute of the OpenAPI object,
and the other is to specify the group name of the currently bound OpenAPI route,
so you need to make sure that the Title parameter is not the same if you call `AddDocRoute` multiple times for the same app instance.

The example code is as follows:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, title="Api Doc")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 1.6.doc_fn_dict
`doc_fn_dict` is a dictionary with the OpenAPI UI name as Key and the OpenAPI Html content generation function as Value.
If this parameter is not passed, then by default `AddDocRoute` will use the following dictionary.
```Python
from any_api.openapi.web_ui.elements import get_elements_html
from any_api.openapi.web_ui.rapidoc import get_rapidoc_html, get_rapipdf_html
from any_api.openapi.web_ui.redoc import get_redoc_html
from any_api.openapi.web_ui.swagger import get_swagger_ui_html

default_doc_fn_dict = {
    "elements": get_elements_html,
    "rapidoc": get_rapidoc_html,
    "rapipdf": get_rapipdf_html,
    "redoc": get_redoc_html,
    "swagger": get_swagger_ui_html,
}
```

Among them, the Key specified in `doc_fn_dict` is a string and the Value is the following function:
```Python
def demo(url: str, title: str = "") -> str:
    pass
```
The first parameter of the function is the OpenAPI Json URL, while the second parameter is the Title,
and `AddDocRoute` will be registered to the app instance via `doc_fn_dict` with Key as url and Value as route function when generating the route.


The following is an example of adding a custom OpenAPI UI Route:
=== "Flask"

    ```py linenums="1" hl_lines="31-39"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    app.listen(8000)
    IOLoop.instance().start()
    ```
It first creates a `demo` function that conforms to the specification, then adds to the default `default_doc_fn_dict`,
and finally binds to the app instance via `AddDocRoute`.

The customized OpenAPI UI page can now be accessed via `http://127.0.0.1:8000/demo`.
### 1.7.OpenAPI
By default, `AddDocRoute` creates an OpenAPI object and generates json content from the OpenAPI object.

!!! note
    The Title of the created OpenAPI object is overwritten by the `title` parameter specified by `AddDocRoute` and the Host bound to the current APP instance is appended to the `Server List`.


However, `AddDocRoute` also supports passing defined OpenAPI objects via the `openapi` parameter, which is used as follows:
=== "Flask"

    ```py linenums="1" hl_lines="31-35"

    --8<-- "docs_source_code/introduction/flask_demo.py::29"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/introduction/starlette_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/introduction/sanic_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/introduction/tornado_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    app.listen(8000)
    IOLoop.instance().start()
    ```

Run the example code and visit [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger),
can see the document description and version number in the upper left corner of the page have changed.











## 2.Template variables for OpenAPI routing
Most interfaces have an authentication mechanism, for example, need to bring the correct Token parameter to get the data properly.
If request data on the OpenAPI page, need to paste the Token parameter every time, which is very inconvenient.
This is where you can use template variables to allow the OpenAPI page to automatically fill in the values of the variables, as shown in the following code:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/openapi_route/flask_demo.py" hl_lines="4 10"

    --8<-- "docs_source_code/openapi/openapi_route/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/openapi_route/starlette_demo.py" hl_lines="4 13"
    --8<-- "docs_source_code/openapi/openapi_route/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/openapi_route/sanic_demo.py" hl_lines="4 11"
    --8<-- "docs_source_code/openapi/openapi_route/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/openapi_route/tornado_demo.py" hl_lines="3 11"
    --8<-- "docs_source_code/openapi/openapi_route/tornado_demo.py"
    ```

First introduced `TemplateVar` class and then used `TemplateVar("uid")` in the example attribute of the Field of `uid` so that `Pait` knows that the template variable for the parameter `uid` is `uid`.
Now run the above code and type `http://127.0.0.1:8000/swagger?template-uid=123` in your browser and it will open up as follows:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16506183174491650618317309.png)
As you can see from the diagram, the value of `uid` has been auto-populated with `123` instead of the default value of zero.
The reason `Pait` is able to set the user's value to the corresponding parameter is because the url has an extra string `template-uid=123`.
This way, when the OpenAPI route receives the corresponding request, it realizes that the request carries a variable starting with `template-`, and knows that this is the value that the user has assigned to the template variable `uid`, so when it generates the OpenAPI data, it can set the user's value to the corresponding parameter.
When generating OpenAPI data, the OpenAPI route will automatically append the user-specified value to the parameter of the template variable uid.
