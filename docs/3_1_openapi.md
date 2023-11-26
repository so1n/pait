## 1.Introduction
`Pait` in addition to parameter type conversion and checking,
but also supports the automatic generation of route function OpenAPI data.
You only need to write the code of the route function,
`Pait` can generate the corresponding OpenAPI documentation of the route function,
such as [Documentation Home](/) of the sample code:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo.py" hl_lines="21 23-24 31"

    --8<-- "docs_source_code/introduction/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo.py" hl_lines="23 25-26 32"
    --8<-- "docs_source_code/introduction/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo.py" hl_lines="22 24-25 32"
    --8<-- "docs_source_code/introduction/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo.py" hl_lines="23 26-27 33"
    --8<-- "docs_source_code/introduction/tornado_demo.py"
    ```
After running the code and visiting: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger) in your browser you can see the SwaggerUI page:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1648292884021Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E9%A6%96%E9%A1%B5.png)

As you can see through the page, the data displayed on the Swagger page includes the data of the response object, the data labeled by the `Pait` decorator, and the parameters of the route function.

## 2.OpenAPI properties of route functions
Binding OpenAPI attributes to a route function is very simple,
just need to fill in the `Pait` decorator with the corresponding attributes.
Common route function attribute bindings are in the following code:
```python
from pait.app.any import pait
from pait.model.tag import Tag

demo_tag = Tag("demo tag", desc="demo tag desc")


@pait(
    desc="demo func desc",
    name="demo",
    summary="demo func summary",
    tag=(demo_tag,)
)
def demo() -> None:
    pass
```
The OpenAPI information for the route function is specified through the `Pait` attributes, which do the following:

| Attributes | OpenAPI Attributes | Description                              |
|------------|--------------------|------------------------------------------|
| desc       | description        | Documentation of the interface in detail |
| name       | operation_id       | The name of the interface                |
| summary    | summary            | Brief description of the interface       |
| tag        | tag                | The OpenAPI tag of the interface         |

!!! note
    - 1.In most cases, the `name` attribute is just part of the `operation_id` attribute and `Pait` does not guarantee that `name` is exactly equal to `operation_id`.
    - 2.Tag should be guaranteed to be globally unique

However, the `name` and `desc` attributes can also be obtained from the route function name and the `__doc__` of the route function
For example, the `name` and `desc` attributes of the route function in the following code are consistent with the code above:
```python
from pait.app.any import pait
from pait.model.tag import Tag

demo_tag = Tag("demo tag", desc="demo tag desc")


@pait(
    summary="demo func summary",
    tag=(demo_tag,)
)
def demo() -> None:
    """demo func desc"""
    pass
```


In addition to the above attributes, OpenAPI has an attribute called `deprecated`,
which is primarily used to mark whether an interface has been deprecated.
`Pait` does not directly support the marking of the `deprecated` attribute,
but instead determines whether the `deprecated` of a route function is `True` by using `PaitStatus`,
which is very simple to use, as in the following code:
```python
from pait.app.any import pait
from pait.model.status import PaitStatus


@pait(status=PaitStatus.test)
def demo() -> None:
    pass
```
This code indicates that the route function is under test and `deprecated` is `False`,
for more statuses and whether it is `deprecated` or not see the following table.

| status value        | stage                | deprecated | description                       |
|---------------------|----------------------|------------|-----------------------------------|
| undefined           | default              | `False`    | undefined, default status         |
| design              | development          | `False`    | design                            |
| dev                 | development          | `False`    | development and testing           |
| integration_testing | development          | `False`    | integration testing               |
| complete            | development complete | `False`    | development complete              |
| test                | development complete | `False`    | testing                           |
| pre_release         | release              | `False`    | pre release                       |
| release             | release              | `False`    | release                           |
| abnormal            | offline              | `True`     | Temporary offline                 |
| maintenance         | offline              | `False`    | Maintenance                       |
| archive             | offline              | `True`     | archive                           |
| abandoned           | offline              | `True`     | abandoned, will not be used again |

## 3.The response object of the route function

In the previous introduction, a list of response objects for a route function is defined via `response_model_list`,
which contains one or more response objects.

!!! note

    It is recommended to use only one response object,
    if there is more than one, most non-OpenAPI feature(e.g. plugins) will default to using only the first response object.

`Pait` provides a variety of response objects, as listed below:

| Response Object Name | Description                     |
|----------------------|---------------------------------|
| JsonResponseModel    | Object whose response is Json   |
| XmlResponseModel     | Object whose response is Xml    |
| TextResponseModel    | Objects whose response is text  |
| HtmlResponseModel    | Objects whose response is Html  |
| FileResponseModel    | Objects whose response is  File |

`Pait` only provides response objects for common response types, if there is no applicable response object,
can define a response object that meets the requirements through `pait.model.response.BaseResponseModel`.
which is a container for the different properties of the OpenAPI response object, as follows.

| Attribute Name | Description                                                                                                                         |
|----------------|-------------------------------------------------------------------------------------------------------------------------------------|
| response_data  | Define the response data, if it is response data with a structure then it should be a `pydantic.BaseModel` describing the structure |
| media_type     | The `Media Type` of the response object                                                                                             |
| name           | The name of the response object.                                                                                                    |
| description    | The description of the response object                                                                                              |
| header         | The header of the response object, the value should be `pydantic.BaseModel` not `Dict`                                              |
| status_code    | The Http status code of the response object, defaults to `(200, )`                                                                  |
| openapi_schema | The [openapi.schema](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#schema-object) of the response object |

Most response objects can be defined through these properties. The sample code is as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/flask_demo.py" hl_lines="12-31 34"

    --8<-- "docs_source_code/openapi/how_to_use_openapi/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/starlette_demo.py" hl_lines="14-33 36"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/sanic_demo.py" hl_lines="13-32 35"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/tornado_demo.py" hl_lines="13-32 36"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/tornado_demo.py"
    ```

The first highlighted code is a response object which indicates that the Http status codes may be 200, 201 and 404.
The `Media Type` is `application/json`.
The Header has properties `X-Token` and `Content-Type`.
And most importantly, the data structure of the response body is defined as follows:
```json
{
  "code": 0,
  "msg": "",
  "data": [
    {
      "name": "so1n",
      "sex": "man",
      "age": 18
    }
  ]
}
```
The second highlighted code binds the response object to the route function.
Now run the code and visit [127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc#tag/default/operation/demo_get) in your browser,
you can see that the current page displays the OpenAPI data of the route function in full, as follows
![](https://fastly.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16867985131801686798512631.png)

!!! note
    Since `Redoc` presents data in a much more parsimonious way than `Swagger`, this case uses `Redoc` to present data.
    In fact `Pait` supports a variety of OpenAPI UI pages, see [OpenAPI routes](/3_2_openapi_route/) for details:.

## 4.Field
The page in the previous section contains not only the data of the response object,
but also the data of the request parameters.
such as the `uid` parameter, which is declared as `required` and is also declared to be of type `integer` with a value in the range of 10-1000.

These request parameters are declared through `Field` objects,
which not only validate the parameters but also provide data for OpenAPI.
In addition to this, the `Field` object has some properties that are specialized for `OpenAPI`, they include:

| Attributes            | description                                                                                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| links                 | OpenAPI link function, used to specify parameters associated with a response object                                                                                                 |
| media_type            | Defines the `Media Type` of a parameter, currently only `Body`, `Json`, `File`, `Form`, `MultiForm` are used, it is recommended to use only one `Media Type` for an route function. |
| openapi_serialization | Define the `serialization` of the parameters, please refer to [serialization](https://swagger.io/docs/specification/serialization/)                                                 |
| example               | Define an example value for the parameter; `Pait` supports factory functions, but converting to OpenAPI will result in a fixed value generated in the moment                        |
| openapi_include       | If the value is `False`, `Pait` will not consider this parameter when generating the Open API                                                                                       |

### 4.1.Links
Links is a feature of OpenAPI that is used to specify that a request parameter from interface A is associated with a piece of data in the response object from interface B. For example:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/flask_link_demo.py" hl_lines="27 38"

    --8<-- "docs_source_code/openapi/how_to_use_openapi/flask_link_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/starlette_link_demo.py" hl_lines="29 43-47"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/starlette_link_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/sanic_link_demo.py" hl_lines="28 40-44"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/sanic_link_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/tornado_link_demo.py" hl_lines="28 45-49"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/tornado_link_demo.py"
    ```

This example defines a login route function--`login_route` and a route function to get user details -- `get_user_route`.
The route function to get the user details needs a token parameter to verify the user and get the user id,
which is generated by the login route function,
so the token parameter of the user details route function is related to the token in the response data of the login route function.

In order for OpenAPI to recognize that the token parameter is associated with a token in the response object.
First create an instance named `link_login_token_model` that is bound to the `LoginRespModel` response object and indicates the parameter to be bound by the expression `$response.body#/data/token"`.
Then the `link_login_token_model` is assigned to the `links` attribute of the `Field` of the `token` in the `get_user_route` route function, and this completes the association once.

After running the code and visiting [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger) in your browser you will see the following page:
![](https://fastly.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16868942366701686894235797.png)
can see through the page that the `Response` column of the login interface shows the `Links` data on the far right.

!!! note
    Currently, many OpenAPI tools only provide simple Links support. For more information on the use and description of Links, see [Swagger Links](https://swagger.io/docs/specification/links/).

## 5.OpenAPI generation

In the OpenAPI ecosystem, at its core is a piece of OpenAPI-conforming json or yaml text,
which can be used in OpenAPI pages such as Swagger, or imported for use in tools such as Postman.
`Pait` will delegate the collected data to [AnyAPI](https://github.com/so1n/any-api) to be processed and generate an OpenAPI object, which supports being converted into a variety of human-readable text or pages.

!!! note
    [AnyAPI](https://github.com/so1n/any-api) is separated from `Pait` and is currently for `Pait` use only, more features will be added to [AnyAPI](https://github.com/so1n/any-api) in subsequent releases.


The following is an example of generating an OpenAPI object and generating output content based on the OpenAPI object:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/flask_with_output_demo.py" hl_lines="35-40 43 45-48"

    --8<-- "docs_source_code/openapi/how_to_use_openapi/flask_with_output_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/starlette_with_output_demo.py" hl_lines="53-58 61 63-66"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/starlette_with_output_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/sanic_with_output_demo.py" hl_lines="54-59 62 64-67"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/sanic_with_output_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/tornado_with_output_demo.py" hl_lines="52-57 60 62-65"
    --8<-- "docs_source_code/openapi/how_to_use_openapi/tornado_with_output_demo.py"
    ```


The first step in the sample code is to create `openapi_model`,
which in the process of creation will get the `app` corresponding interface and data.
The second step is to call the `content` method of `openapi_model`, which has a `serialization_callback` parameter with a default value of `json.dump`.
So a direct call to `openapi_model.content()` will generate the following JSON text.


??? note "Json example (the example text is long, please open it as needed)"

    ```json

    --8<-- "docs_source_code/openapi/how_to_use_openapi/openapi.json"
    ```

In addition, the sample code also customizes a function that serializes to yaml -- `my_serialization` and generates the following yaml text via `openapi_model.content(serialization_callback=my_serialization)`:

??? note "Yaml example (the example text is long, please open it as needed)"

    ```yaml

    --8<-- "docs_source_code/openapi/how_to_use_openapi/openapi.yml"
    ```
Finally, the `Markdown` method of [AnyAPI](https://github.com/so1n/any-api) is also used to generate Markdown documents in different languages.

??? note "Chinese Markdown example(The sample text is long, please open it as needed, and only show the original data)"

    ```markdown

    --8<-- "docs_source_code/openapi/how_to_use_openapi/openapi_zh_cn.md"
    ```


??? note "English Markdown example (the sample text is long, please open it as needed, and only display the original data)"



    ```markdown

    --8<-- "docs_source_code/openapi/how_to_use_openapi/openapi_en.md"
    ```
