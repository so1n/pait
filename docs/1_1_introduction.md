# Introduction
`Pait` is an auxiliary framework and it will not change the usage of Web frameworks.
Therefore, before introducing the use of `Pait`, let's first take a look at the usage of different Web frameworks.

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_hello_world_demo.py"

    --8<-- "docs_source_code/introduction/flask_hello_world_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/starlette_hello_world_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/sanic_hello_world_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/tornado_hello_world_demo.py"
    ```

The logic of this sample code is consistent with the sample code on the homepage.
The main feature of the sample code is to register a route into an instance of the Web framework at startup,
and after receiving a request with the URL `/api` and method `POST` at runtime, the request will be handed over to the route function for processing.
The logic of the route function is also very simple.
It will verify the data first and return the data only if it meets the requirements. Otherwise, an error will be thrown directly.

Next, we will use `Pait` in the example code. Their functions are the same, as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo.py" hl_lines="10 12 13"

    --8<-- "docs_source_code/introduction/flask_demo.py::7"


    @pait()
    --8<-- "docs_source_code/introduction/flask_demo.py:22:30"
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo.py" hl_lines="12 14 15"
    --8<-- "docs_source_code/introduction/starlette_demo.py::9"


    @pait()
    --8<-- "docs_source_code/introduction/starlette_demo.py:24:31"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo.py" hl_lines="11 13 14"
    --8<-- "docs_source_code/introduction/sanic_demo.py::8"


    @pait()
    --8<-- "docs_source_code/introduction/sanic_demo.py:23:31"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo.py" hl_lines="23 26-27 33"
    --8<-- "docs_source_code/introduction/tornado_demo.py"
    ```

The `@pait` decorator of the first highlighted code in the sample is the core of all functions of `Pait`.
After using `@pait` to decorate the route function, `Pait` will get the function signature through `inspect` and generate Dependency injection rules.
For example, the parameters of the route function in the second highlighted code are all filled in with key parameters in the format of `<name>:<type>=<default>`.
`Pait` automatically transforms key parameters into its own dependency injection rules at initialization time with the following rules:

| Key     | Meaning                  | Feature                                                                                                                                                                                |
|---------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name    | Parameter Name           | `Pait` will use name as the key to get the corresponding value from the requested resource.                                                                                            |
| type    | Parameter Type           | Used for parameter verification or conversion                                                                                                                                          |
| default | `Field` object of `Pait` | Different `Field` types represent obtaining values from different request types; the properties of the `Field` object tell `Pait` how to get the value from the request and verify it. |

Taking the `uid` parameter above as an example,
first, `Pait` will get json data from the request obj.
Second , use `uid` as the key to get the corresponding value from the json data and convert and verify whether it is` int` type.
Last, determine whether the value is between 10-1000, if not, an error will be reported directly, if so, it will be assigned to the `uid` variable.

By comparing the first sample code with the code after using `Pait`,can see that the code after using `Pait` is simpler, clearer
and also improves the robustness of the code.



!!! note
    When using `Json()` , `mypy` will detect a type mismatch, so you can ignore this problem through `Json.i()`.
    If you need `mypy` to check the values of `default`, `default_factory` and `example` attributes in `Json`, it is recommended to use `Json.t()` directly.
