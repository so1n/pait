The core of `Pait` is a decorator, this decorator is only responsible for the assembly and arrangement of plugins,
and really responsible for the implementation of the function are these plugins that are initialized by the decorator,
of which `Pait`'s type conversion and validation belong a core plugin of `Pait` -- `ParamPlugin`.

## Brief Introdction
In addition to the core plugins, plugins can be divided into two main categories,
pre plugins that inherit from `PrePluginProtocol` and post plugins that inherit from `PostPluginProtocol`.

Developers can use plugins that need to be enabled via `Pait`, after the program is started,
`Pait` will initialize the plugins in order in the form of an interceptor,
if the plugin is a pre-plugin then it will be placed before the core plugin,
otherwise it will be placed after the core plugin (post-plugin).

In addition to the different parent classes inherited by the pre-plugin and the post-plugin,
the main difference between them is that the parameters they get when they are called are different.
In this case, the pre-plugin gets the request parameters passed by the web framework (which can be thought of as a simple middleware),
while the post-plugin gets the request data converted by the `Pait` core plugin, as exemplified by the following function:
```Python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
Assuming that the `app` in the code has been loaded with a middleware and the corresponding `Pait` plugin,
when a request is received,
it will process the request in the following order (using a different way of describing the processing logic, the core logic is the same):

=== "graph"

    ``` mermaid
    graph LR
      A[client] --> |send request| B[Middleware];
      B --> |recv response| A;
      B -->  C{Find match route?};
      C --> |Yes| D[Pre Plugin];
      C --> |No| B;
      D --> B;
      D --> E[Core Plugin];
      E --> D;
      E --> F[Post Plugin];
      F --> E;
      F --> G[Route Function];
      G --> F;
    ```

=== "sequence diagram"

    ``` mermaid
    sequenceDiagram
      client->>Middleware: send request
      Middleware->>Route Match: Find match route?
      Route Match->>Middleware: Success or Fail
      Middleware->>client: Route Match Fail, Return Not Found 404
      Middleware->>Pre Plugin: Route Match Success, send Request obj
      Pre Plugin->>Core Plugin:  send Request obj
      Core Plugin->>Post Plugin: send Param:{"uid": "", "user_name":""}
      Post Plugin->>Route Function: send Param:{"uid": "", "user_name":""}
      Route Function->>Post Plugin: recv Response obj
      Post Plugin->>Core Plugin: recv Response obj
      Core Plugin->>Pre Plugin: recv Response obj
      Pre Plugin->>Middleware: recv Response obj
      Middleware->>client: recv Response obj
    ```

=== "jpg"

    ![pait-plugin](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1647762511992pait-plugin.jpg)


In this logic, the request is first processed by the Web framework's middleware,
then the Web framework looks for a route and returns a `Not Found` response to the client if no route can be found,
and passes the request to `Pait` to process if a corresponding route is found.
The processing at `Pait` can be divided into the following steps:

- 1.The request will be processed by the Pre plugin, at this time the Pre plugin can only get the `request` parameter corresponding to the framework (or not if it is a `flask` framework) and the `Path` parameter.
- 2.When the Pre plugin processing is complete, the request will be passed to the core plugin for parameter extraction and checksum conversion.
- 3.After processing by the core plugin will pass the extracted parameters to the Post plugin, which will be processed by the Post plugin.
- 4.Finally by the Post plugin parameters to the real route function to generate a response and return one by one.

## How to use
Currently `Pait` receives pre-plugins and post-plugins via `plugin_list` and `post_plugin_list` as follows:
```Python
from pait.app.any import pait
from pait.plugin.required import RequiredPlugin

@pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["username"]})])
```
The sample code uses a post plugin named `RequiredPlugin`, which needs to be used through the `post_plugin_list` parameter.
At the same time, the plugin needs to be `Pait` orchestrated before you can use,
so the plugin does not support the `__init__` method initialization, but need to use the `build` method to initialize the plugin.

If reuse of the plugin, it is recommended to use the `create_factory` function,
which uses [PEP-612](https://peps.python.org/pep-0612/) to support IDE and type checking, `create_factory` is used as follows:
```Python
from pait.app.any import pait
from pait.util import create_factory
from pait.plugin.required import RequiredPlugin

# Pass in the plugin's build method and fill in the parameters needed for build to get a plugin build factory function
required_plugin = create_factory(RequiredPlugin.build)(required_dict={"email": ["username"]})

# Calling `required_plugin` will get a separate plugin that will not be shared with other functions
@pait(post_plugin_list=[required_plugin()])
def demo_1():
    pass

@pait(post_plugin_list=[required_plugin()])
def demo_2():
    pass
```

## Turn off pre check
`Pait` is a decorator used to decorate the route function,
so it loaded with various parameters and initialized at program startup.
However, the plugin's `pre_check_hook` method is called before initialization to check if the plugin is being used correctly,
as in the following code.
```Python
from pait.app.any import pait
from pait.field import Body

@pait()
def demo(
    uid: str = Body.i(default=None)
) -> None:
    pass
```
At program startup the core plugin checks that the `default` value is not of type `str`, so an error is thrown.
However, `pre-check` may affect the startup time of the program, so it is recommended to do `pre_check` only in test environments,
and turn it off in production environments.
It can be turned off by setting the environment variable `PAIT_IGNORE_PRE_CHECK` to True.
