There is a lot of parameter verification logic inside `Pait`, so a variety of error conditions will occur.
In order to easily catch and understand exceptions during use, `Pait` has a simple exception mechanism.

!!! note
    Exceptions of `Pait` are inherited from `PaitBaseException`,
    and in the event of an exception can use `isinstance(exc, PaitBaseException)` to determine if the exception is a `Pait` exception.
    In addition, since `Pait` passes the data to `Pydantic` for validation, `Pydantic` related exceptions will be thrown at runtime because the validation fails, you can learn how to use `Pydantic` exceptions through [Error Handling](https://pydantic-docs.helpmanual.io/usage/models/#error-handling).

## 1.`Pait` exception introduction
### 1.1.TipException

When the program is running, `Pait` checks and verifies the parameters, and throws an exception if the verification fails.
However, the exception will only flow in `Pait` and will not be exposed so that the developer will not be able to know which route function threw the exception,
which makes troubleshooting very difficult.

So `Pait` wraps the exception in a `TipException` that indicates which route function threw the exception and where it threw it.
If you use an IDE tool such as `Pycharm`, you can also click on the route to jump to the corresponding place, an example of an exception is as follows:
```bash
Traceback (most recent call last):
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/exceptions.py", line 71, in __call__
    await self.app(scope, receive, sender)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 583, in __call__
    await route.handle(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 243, in handle
    await self.app(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 54, in app
    response = await func(request)
  File "/home/so1n/github/pait/pait/core.py", line 232, in dispatch
    return await first_plugin(*args, **kwargs)
  File "/home/so1n/github/pait/pait/param_handle.py", line 448, in __call__
    async with self:
  File "/home/so1n/github/pait/pait/param_handle.py", line 456, in __aenter__
    raise e from gen_tip_exc(self.call_next, e)
  File "/home/so1n/github/pait/pait/param_handle.py", line 453, in __aenter__
    await self._gen_param()
  File "/home/so1n/github/pait/pait/param_handle.py", line 439, in _gen_param
    self.args, self.kwargs = await self.param_handle(func_sig, func_sig.param_list)
  File "/home/so1n/github/pait/pait/param_handle.py", line 396, in param_handle
    await asyncio.gather(*[_param_handle(parameter) for parameter in param_list])
  File "/home/so1n/github/pait/pait/param_handle.py", line 393, in _param_handle
    raise gen_tip_exc(_object, closer_e, parameter)
pait.exceptions.TipException: Can not found content__type value for <function raise_tip_route at 0x7f512ccdebf8>   Customer Traceback:
    File "/home/so1n/github/pait/example/param_verify/starlette_example.py", line 88, in raise_tip_route.
```
Through the exception example, can see that the exception is thrown through the `gen_tip_exc` function,
and the thrown exception information includes the location of the route function.
However, there is a downside to using `TipException` though,
it causes all exceptions to be `TipException` needing to get the original exception via `TipException.exc`.
### 1.2.Parameter exception
Currently, `Pait` has 3 types of parameter exceptions, as follows:

| Exception               | Location                 | Description                                                      |
|-------------------------|--------------------------|------------------------------------------------------------------|
| NotFoundFieldException  | Plugin Pre Check         | Indicates that the corresponding `Field` cannot be matched, and this exception will not be encountered during normal use.                               |
| NotFoundValueException  | Execute route function | This exception indicates that the corresponding value cannot be found from the request data. This is a common exception.                                    |
| FieldValueTypeException | Plugin Pre Check         | Indicates that `Pait` found that the values filled in `default`, `example` in `Field` are illegal, and the user needs to make corrections according to the prompts.|

These three exceptions are inherited from `PaitBaseParamException`, and its source code is as follows:
```Python
class PaitBaseParamException(PaitBaseException):
    def __init__(self, param: str, msg: str):
        super().__init__(msg)
        self.param: str = param
        self.msg: str = msg
```
It can be seen from the code that `PaitBaseParamException` not only includes error information,
but also includes the name of the parameter that caused the current error.

## 2.How to use exceptions
### 2.1.Usage Exception
In CRUD business, exceptions thrown by route functions must be caught, and then an agreed error message is returned for front-end use.
The following is an example code for exception capture:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/exception/flask_with_exception_demo.py"  hl_lines="11 14 16 21"

    --8<-- "docs_source_code/introduction/exception/flask_with_exception_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/exception/starlette_with_exception_demo.py"   hl_lines="14 17 19 24 35"
    --8<-- "docs_source_code/introduction/exception/starlette_with_exception_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/exception/sanic_with_exception_demo.py"    hl_lines="11 14 16 18 21"
    --8<-- "docs_source_code/introduction/exception/sanic_with_exception_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/exception/tornado_with_exception_demo.py" hl_lines="14 17 19 24"
    --8<-- "docs_source_code/introduction/exception/tornado_with_exception_demo.py"
    ```

The exception handling of the `api_exception` function in the sample code is arranged in a strict order.
It is generally recommended to handle exceptions in this order.

The first highlighted code of the `api_exception` function is to extract the original exception of `TipException`.
All subsequent exception handling is for the original exception, so it has the highest priority.
The second highlighted code is to handle all `Pait` parameter exceptions.
It will extract parameter information and error information and inform the user which parameter has an error.
The third highlighted code handles the verification exception of `Pydantic`.
It will parse the exception and return the parameter information that failed the verification.
The fourth piece of code handles all exceptions of `Pait`, which usually occur rarely.
The last step is to handle exceptions in other situations, which may be exceptions defined by the business system.

The last highlighted code is to mount the custom `api_exception` function into the framework's exception handling callback through the exception mechanism of the Web framework.

!!! note
    `Tornado`'s exception handling is implemented in `RequestHandler`.

After running the code and calling the `curl` command can know:

- When parameters are missing, an error message indicating that the parameter cannot be found will be returned.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo"
    {"code":-1,"msg":"error param:demo_value, Can not found demo_value value"}
    ```
- When parameter verification fails, the parameter name with verification error will be returned.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=a"
    {"code":-1,"msg":"check error param: ['demo_value']"}
    ```
- Normal data is returned when the parameters are normal.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=3"
    {"code":0,"msg":"","data":3}
    ```


!!! note "Protocol description"
    The response of the sample code uses common front-end and back-end interaction protocols:
    ```json
    {
      "code": 0,  # When it is 0, it means the response is normal, if it is not 0, it means it is abnormal.
      "msg": "",  # It is an error message when there is an exception, and it is empty when it is normal.
      "data": {}  # Response Data
    }
    ```


### 2.2.Custom TipException
The TipExceptions are enabled by default.
If you think that error prompts will consume performance or want to turn off it,
can define the `tip_exception_class` attribute of `ParamHandler` as `None` to turn off exception prompts. code show as below:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/exception/flask_with_not_tip_exception_demo.py"  hl_lines="11 12 15 29"

    --8<-- "docs_source_code/introduction/exception/flask_with_not_tip_exception_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/exception/starlette_with_not_tip_exception_demo.py"   hl_lines="14 15 18 32"
    --8<-- "docs_source_code/introduction/exception/starlette_with_not_tip_exception_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/exception/sanic_with_not_tip_exception_demo.py"    hl_lines="11 12 15 29"
    --8<-- "docs_source_code/introduction/exception/sanic_with_not_tip_exception_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/exception/tornado_with_not_tip_exception_demo.py" hl_lines="13 14 18 33"
    --8<-- "docs_source_code/introduction/exception/tornado_with_not_tip_exception_demo.py"
    ```

The sample code has a total of three modifications:
    - The `NotTipParamHandler` in the first highlighted code is inherited from `ParamHandler` (or `AsyncParamHandler`),
        which turns off exception tip by setting the `tip_exception_class` attribute to empty.
    - The second piece of highlighting code removes the `TipException` extraction logic from the `api_exception` function, as it is not needed now.
    - The third piece of highlighted code defines the `ParamHandler` used by the current route function to be a `NotTipParamHandler` via the `param_handler_plugin` property of `Pait`.


After running the code and calling the `curl` command can know:

- When parameters are missing, an error message that the parameter cannot be found will be returned.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo"
    {"code":-1,"msg":"error param:demo_value, Can not found demo_value value"}
    ```
- When parameter verification fails, the parameter name with verification error will be returned.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=a"
    {"code":-1,"msg":"check error param: ['demo_value']"}
    ```
- Normal data is returned when the parameters are normal.
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=3"
    {"code":0,"msg":"","data":3}
    ```
