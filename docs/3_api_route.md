# APIRoute - Route Management

As an API project grows, route management becomes increasingly complex. Traditional route registration often separates
route handlers from route registration code, which can make the codebase scattered and hard to maintain.
`Pait` provides the `APIRoute` class to manage routes declaratively, offering a more organized route management model.

## 1.APIRoute introduction

`APIRoute` is a high-level route management tool provided by `Pait`. It lets developers organize and manage API routes in
a declarative way. Compared with traditional route registration, `APIRoute` provides the following advantages:

- **Declarative route definition**: Declare route information directly with decorators on route functions
- **Hierarchical route organization**: Support route groups and nested routes for large projects
- **Class-based view support**: Support CBV (Class-Based Views)
- **Shared route configuration**: Configure common parameters for a group of routes
- **Route reuse**: Include and compose sub routes

This design is similar to FastAPI-style route management and gives `Pait` users a more modern development experience.

## 2.Basic usage

The basic usage of `APIRoute` is straightforward: create an `APIRoute` instance, then define routes with HTTP method
decorators.

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_basic_demo.py"
    --8<-- "docs_source_code/api_route/flask_basic_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_basic_demo.py"
    --8<-- "docs_source_code/api_route/starlette_basic_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_basic_demo.py"
    --8<-- "docs_source_code/api_route/sanic_basic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_basic_demo.py"
    --8<-- "docs_source_code/api_route/tornado_basic_demo.py"
    ```

The examples above show the three main steps:

1. **Create an APIRoute instance**: Use `APIRoute(path="/api")` to create a route group with a base path
2. **Use HTTP method decorators**: Use decorators such as `@api_route.get()` and `@api_route.post()` to define routes
3. **Inject routes into the app**: Call `api_route.inject(app)` to register all routes with the web framework app

Compared with traditional route registration, this keeps route definitions and route handlers close to each other, making
the code easier to read and maintain.

## 3.HTTP method support

`APIRoute` supports common HTTP methods. Each method can be used through the corresponding decorator:

- `@api_route.get(path)`: Define a GET handler
- `@api_route.post(path)`: Define a POST handler
- `@api_route.put(path)`: Define a PUT handler
- `@api_route.delete(path)`: Define a DELETE handler
- `@api_route.patch(path)`: Define a PATCH handler
- `@api_route.head(path)`: Define a HEAD handler
- `@api_route.options(path)`: Define an OPTIONS handler
- `@api_route.trace(path)`: Define a TRACE handler

Each decorator supports the same parameters as the `Pait` decorator, such as `response_model_list`, `tag`, and `desc`.

## 4.Dynamic route registration

In addition to decorators, `APIRoute` also supports dynamic route registration with `add_api_route`:

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_dynamic_route_demo.py"
    --8<-- "docs_source_code/api_route/flask_dynamic_route_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_dynamic_route_demo.py"
    --8<-- "docs_source_code/api_route/starlette_dynamic_route_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_dynamic_route_demo.py"
    --8<-- "docs_source_code/api_route/sanic_dynamic_route_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_dynamic_route_demo.py"
    --8<-- "docs_source_code/api_route/tornado_dynamic_route_demo.py"
    ```

This is useful when routes need to be generated dynamically or registered conditionally.

## 5.Sub routes and route composition

For large projects, grouping routes by feature module is a good practice. `APIRoute` supports composing sub routes, so
routes maintained by different modules can be merged into a single entry point.

A common structure is to define one `APIRoute` per business module, such as users, orders, or payments. The application
entry point can then create a main `APIRoute` with a common prefix and combine these module routes with
`include_sub_route`. This lets module files focus on their own paths and parameters without repeating the global prefix,
common tags, or common group configuration.

The following examples show how to compose user routes, order routes, and a main route:

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_advanced_demo.py"
    --8<-- "docs_source_code/api_route/flask_advanced_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_advanced_demo.py"
    --8<-- "docs_source_code/api_route/starlette_advanced_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_advanced_demo.py"
    --8<-- "docs_source_code/api_route/sanic_advanced_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_advanced_demo.py"
    --8<-- "docs_source_code/api_route/tornado_advanced_demo.py"
    ```

The advanced examples demonstrate several important concepts.

### 5.1.Route grouping

Create different `APIRoute` instances to manage different feature modules:

- `user_api_route` manages user-related APIs
- `order_api_route` manages order-related APIs

Each sub route can have its own `path`, `tag`, `group`, `desc`, and other `Pait` configuration. Routes inside a module
only need to declare relative paths, such as `user_api_route.get("/profile")`; the parent prefix is added when the sub
route is included by the main route.

### 5.2.Include sub routes

Use `include_sub_route` to include sub routes in the main route:

```python
main_api_route = APIRoute(path="/api/v1").include_sub_route(user_api_route, order_api_route)
```

`include_sub_route` can receive multiple sub routes at once and can also be chained. A sub route must contain at least one
route before it is included; otherwise `Pait` raises an exception to avoid silently registering an empty module.

### 5.3.Path merging

The child route path is automatically merged with the parent route path. For example:

- Parent route path: `/api/v1`
- User route path: `/user`
- Final profile route path: `/api/v1/user/profile`

Path merging handles `/` boundaries to avoid duplicate slashes. OpenAPI paths and framework-specific paths are handled by
the framework adapter during injection. For example, different frameworks use different path parameter syntax, and
`APIRoute` delegates that conversion to the corresponding adapter.

### 5.4.Configuration merging

When sub routes are included, `APIRoute` also merges route configuration. Normal configuration keeps the value closest to
the concrete route. Configuration keys prefixed with `append_` are appended, such as `append_tag`, `append_author`, and
`append_response_model_list`. This is useful when the parent route should add common tags or response models while each
child route keeps its own business tags.

This hierarchical route organization keeps the API structure clearer and easier to maintain in large projects.

## 6.Class-Based View support

`APIRoute` supports Class-Based Views (CBV). This is useful when multiple HTTP methods for the same resource need to
share state, reuse methods, or stay grouped in one class. For example, `GET /users` and `POST /users` can be implemented
in the same `UserAPIView`, and class attributes or instance methods can act as shared context for those HTTP methods.

Different web frameworks use different CBV base classes: Flask usually uses `MethodView`, Starlette uses `HTTPEndpoint`,
Sanic uses `HTTPMethodView`, and Tornado uses `RequestHandler`. `APIRoute.add_cbv_route` adapts to these CBV types and
registers HTTP methods from the class under the same route path.

### 6.1.Basic CBV usage

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_cbv_demo.py"
    --8<-- "docs_source_code/api_route/flask_cbv_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_cbv_demo.py"
    --8<-- "docs_source_code/api_route/starlette_cbv_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_cbv_demo.py"
    --8<-- "docs_source_code/api_route/sanic_cbv_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_cbv_demo.py"
    --8<-- "docs_source_code/api_route/tornado_cbv_demo.py"
    ```

### 6.2.CBV advantages

- **Code organization**: Related HTTP methods can be grouped in the same class
- **Shared state**: Class instances can share attributes and methods
- **Inheritance support**: Shared logic can be reused through inheritance
- **Middleware-style handling**: Common processing can be implemented at the class level

### 6.3.How Pait handles CBV

When `add_cbv_route` is called, `APIRoute` records the CBV class, route path, and `Pait` parameters. During `inject(app)`,
the framework adapter processes these CBV methods. For HTTP methods that are not explicitly decorated with `@pait()`,
`APIRoute` automatically applies a `Pait` decorator, so those methods can still use fields such as `Header.i()` and
`Json.i()`.

If an HTTP method needs its own configuration, such as `response_model_list`, `tag`, `desc`, `summary`, or plugin lists,
decorate that method with `@pait(...)` directly. Class-level or `add_cbv_route` configuration is better suited for shared
settings.

### 6.4.CBV notes

- The CBV class must inherit from a CBV base class supported by the current framework, otherwise injection fails.
- HTTP method names should be lowercase, such as `get`, `post`, `put`, and `delete`.
- The `path` passed to `add_cbv_route` is the route path for the whole CBV class, not a separate path for each method.
- For frameworks that need special route parameters, such as Sanic, pass them through `framework_extra_param`.

!!! note
    `add_cbv_route` automatically applies `Pait` handling to HTTP methods that are not decorated with `@pait()`.
    If a method needs its own `response_model_list`, `tag`, `desc`, or other configuration, decorate that method with
    `@pait()` explicitly.

## 7.Route configuration inheritance

`APIRoute` supports configuration inheritance. Sub routes can inherit configuration from their parent route:

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_config_inherit_demo.py"
    --8<-- "docs_source_code/api_route/flask_config_inherit_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_config_inherit_demo.py"
    --8<-- "docs_source_code/api_route/starlette_config_inherit_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_config_inherit_demo.py"
    --8<-- "docs_source_code/api_route/sanic_config_inherit_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_config_inherit_demo.py"
    --8<-- "docs_source_code/api_route/tornado_config_inherit_demo.py"
    ```

In the examples, the parent route provides the default group through `group="main"` and appends the parent tag through
`append_tag=(Tag("api-route-api"),)`. The child route keeps its own `tag=(Tag("api-route-users"),)`. The final route path
is `/api/users/profile`, and the route has both `api-route-users` and `api-route-api` tags.

This configuration inheritance keeps route configuration consistent across the route hierarchy.

### 7.1.Framework route parameters

`APIRoute` also supports `framework_extra_param`, which passes parameters through to the underlying framework route
registration method. For example, Flask can receive `endpoint`, Starlette can receive `name`, Sanic can receive `stream`,
and Tornado can receive `request_handler`.

=== "Flask"

    ```py linenums="1" title="docs_source_code/api_route/flask_framework_extra_demo.py"
    --8<-- "docs_source_code/api_route/flask_framework_extra_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/api_route/starlette_framework_extra_demo.py"
    --8<-- "docs_source_code/api_route/starlette_framework_extra_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/api_route/sanic_framework_extra_demo.py"
    --8<-- "docs_source_code/api_route/sanic_framework_extra_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/api_route/tornado_framework_extra_demo.py"
    --8<-- "docs_source_code/api_route/tornado_framework_extra_demo.py"
    ```

When the parent route, child route, and concrete route all set `framework_extra_param`, the values are merged by level.
Configuration closer to the concrete route has higher priority. `Pait` parameters follow a similar merge rule: sub routes
inherit parent route configuration, and parameters prefixed with `append_` are appended to existing configuration.
