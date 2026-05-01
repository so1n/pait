
The `Field` objects mentioned in the previous section are all related to the request object
and their role is to inject the resources specified by the request object into the route function.
The `Depend` is a special `Field` object that injects functions that conform to the `Pait` rule into the route function, which can do the following:

- Share the same logic
- Implement security verification function
- Interact with other systems (such as databases).

!!! note

    `Depend` only does dependency injection related to the request object,
    and cannot complete dependency injection feture other than the request object.
    If you have this need,
    it is recommended to implement the dependency injection function through DI tools.
    For specific DI tools, see [Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python).

## 1.Use of Depend
Usually, the business system will have the function of user Token verification,
this function is very consistent with the `Depend` usage scenario.
In this scenario,
the user carries a Token every time who accesses the system,
and the server will first determine whether the Token is legal after receiving the user's request,
and if it is legal, it will be released; if it is not legal, system will return an error message.

Most users of micro-web frameworks like `Flask` will choose to use `Python` decorators to solve this problem, as follows:
```python
@check_token()
def demo_route() -> None:
    pass
```
In some cases, additional functionality is added, such as getting the uid data based on the Token and passing it to the route function.
```python
@check_token()
def demo_route(uid: str) -> None:
    pass
```
However, it can be seen that this implementation is more dynamic,
and it can make difficult for code inspection tools to detect if there is a problem with this code.
It is only possible to prevent developers from incorrectly using the `check_token` decorator if you have a good internal specification, but there's nothing it can do to completely prevent the `check_token` decorator from being used incorrectly.

Using `Pait`'s `Depend` can solve this problem. The sample code for `Pait`'s `Depend` is as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_depend_demo.py"  hl_lines="14 17-20 24"

    --8<-- "docs_source_code/introduction/depend/flask_with_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_depend_demo.py"   hl_lines="17 20-23 27"
    --8<-- "docs_source_code/introduction/depend/starlette_with_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_depend_demo.py"    hl_lines="14 17-20 24"
    --8<-- "docs_source_code/introduction/depend/sanic_with_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_depend_demo.py" hl_lines="19 22-25 30"
    --8<-- "docs_source_code/introduction/depend/tornado_with_depend_demo.py"
    ```
The sample code in the first highlighting code is to mimic the database call method,
the current assumption that the database only user `so1n` has a token and the token value is "u12345".
The second highlighted code is a function called `get_user_by_token`,
which is responsible for getting the token from the Header and checking if it exists, if it exists, it returns the user, if it doesn't, it throws an error.
This is a special function that takes the same arguments as the `Pait` decorated route function, so any of the previously mentioned methods can be used in this function.
The third highlighted code is the Token parameter of the route function and what's special here is wrapping the `get_user_by_token` function through `field.Depend`.
so that `Pait` knows that the current Token parameter of the route function must be obtained through the `get_user_by_token` function.


After running the code and calling the `curl` command,
can find that this code works normally. When the token exists, the user name will be returned. If token does not exist, an error message will be returned:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```

In addition, `Pait` can also support multiple levels of Depend nesting.
The above code as an example,
it is now assumed that it is necessary to verify that the Token is legal before going to the database to obtain the corresponding user.
The code can be rewritten as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"  hl_lines="17-20 23"

    --8<-- "docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"   hl_lines="20-23 26"
    --8<-- "docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"   hl_lines="17-20 23"
    --8<-- "docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"    hl_lines="22-25 28"
    --8<-- "docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"
    ```

Sample code in the highlighted code for the modified code, this part of the code is mainly a new `check_token` function used to get and verify the Token.
At the same time `get_user_by_token` to get the source of Token from `Header` to `check_token`.

After running the code and calling the `curl` command to test it, we can see from the output that it will return an error message if it doesn't conform to the checking logic:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:fu12345"
{"data":"Illegal Token"}
```

## 2.Depend based on ContextManager
The `Depends` usages shown in the previous section all work fine,
but they don't have any way to know what's going on with the function like a `Python` decorator does,
including whether the function is running correctly, what exceptions are thrown, when it's done, etc.
At this time, need to solve this problem based on `Depend` of `ContextManager`.

Using `Depend` based on `Context Manager` is very simple,
just add the corresponding `Context Manager` decorator to the function,
and then use the `try`, `except`, `finally` syntax as described in [Context Manager official documentation](https://docs.python.org/3/library/contextlib.html), as shown in the following sample code:
```Python
from contextlib import contextmanager
from typing import Any, Generator

@contextmanager
def demo() -> Generator[Any, Any, Any]:
    try:
        # 1
        yield None
    except Exception:
        # 2
        pass
    finally:
        # 3
        pass
```
The position of sequence number 1 in this sample code is used to normal function logic and return data through yield.
Position number 2 is used to write the code logic when the function runs abnormally.
The last serial number 3 is used to finally processing.

Below is a sample code using `ContextManager` and `Depend`：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"  hl_lines="17-33 36-47 51"

    --8<-- "docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"   hl_lines="20-36 39-50 55"
    --8<-- "docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"  hl_lines="17-33 36-47 52"
    --8<-- "docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"    hl_lines="13-29 32-43 58"
    --8<-- "docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"
    ```

This example assumes that a session is created based on the corresponding uid for each request and that the session is automatically closed at the end of the request.
The first highlighted code simulates a session based on the uid.
The second highlighted code is a `Depends` function decorated with `ContextManger`, which prints different things in `try`, `except` and `finally`.
The third highlighted code is a route function, which will return an error or normal response according to the value of `is_raise`.


Now run the code and use the `curl` command to test.
Through the result output, can find that the response result of the first request is normal, while the second request is abnormal (returns an empty string):
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo?uid=999"
{"code":0,"msg":999}
> curl "http://127.0.0.1:8000/api/demo?uid=999&is_raise=True"
{"data":""}
```
At this time, switch back to the terminal where the sample code has been run, and you can find that the terminal prints data similar to the following:
```bash
context_depend init
context_depend exit
INFO:     127.0.0.1:44162 - "GET /api/demo?uid=999 HTTP/1.1" 200 OK
context_depend init
context_depend error
context_depend exit
INFO:     127.0.0.1:44164 - "GET /api/demo?uid=999&is_raise=True HTTP/1.1" 200 OK
```
It can be seen from the data output by the terminal that in the first request,
the terminal only printed `init` and `exit`,
but in the second request, the terminal printed more between `init` and `exit` One line of `error`.
## 3.基于类的Depend
Class-based `Depend` is similar to function-based `Depend`,
the difference between them is that `Pait` not only resolves the function signature of the class's `__call__` method,
but also resolves the class's attributes, as shown in the following example:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_class_depend_demo.py"  hl_lines="17-26 30"

    --8<-- "docs_source_code/introduction/depend/flask_with_class_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"   hl_lines="20-29 33"
    --8<-- "docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"  hl_lines="17-26 30"
    --8<-- "docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"    hl_lines="22-31 36"
    --8<-- "docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"
    ```
The sample code in the first highlighting code is based on the class `Depend` implementation,
this code is divided into two main parts.
The first part is the attributes of the class, which also uses the format of `<name>: <type> = <default>`,
whenever a request hits the route, `Pait` will be injected into the class with the corresponding value.
The second part of the code is rewritten from the example in `Usage of Depend`,
it will check the Token and the corresponding username (normal logic basically doesn't do this, it's just a functional demonstration here),
and the `__call__` method is used in a similar way to the function-based `Depend`.

??? tip "`__call__` method usage restrictions"
    Everything in `Python` is an object, so a class with a `__call__` method is similar to a function, as shown in the following example code:
    ```Python
    from typing import Any

    class DemoDepend(object):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            pass
    ```
    The `__call__` method in the code is an intuitive way to use, but due to the limitations of `Python`,
    the `__call__` method does not support rewriting function signature, such as the following example:
    ```Python
    from typing import Any
    from pait import field

    class DemoDepend(object):
        def __init__(self) -> Any:
            def new_call(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any:
                pass
            setattr(self, "__call__", new_call)

        def __call__(self, uid: str = field.Query.i()) -> Any:
            pass
    ```
    After the class is instantiated, the function signature of the `__call__` method parsed by `inspect` is still `__call__(self, uid: str = field.Query.i()) -> Any` instead of `__call__(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`.
    This causes `Pait` to fail to extract the correct parameter rules.
    In order to solve this problem,
    `Pait` prioritizes parsing `pait_handler` methods that are allowed to be overridden, as follows.:
    ```Python
    from typing import Any
    from pait import field

    class DemoDepend(object):
        def __init__(self) -> Any:
            def new_call(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any:
                pass
            setattr(self, "pait_handler", new_call)

        def pait_handler(self, uid: str = field.Query.i()) -> Any:
            pass
    ```
    After the class is instantiated, `Pait` parses out that the function signature of `pait_handler` is `pait_handler(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`

In the second highlighted code, the function-based `Depend` in the `Depend` parameter is replaced with the class-based `Depend`.

After running the code and executing the following `curl` command, can see the following output:
<!-- termynal -->
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"data":"Can not found user_name value"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=so1n" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=faker" --header "token:u12345"
{"data":"The specified user could not be found through the token"}
```

??? tip "Initialization for class-based `Depend`"

    Since a new instance is created for each request, this means that cannot customize the initialization parameters as usual.
    At this time, can use `pait.util.partial wrapper` to bind initialization parameters, as shown in the following example:

    ```python
    from pait import field
    from pait.util import partial_wrapper

    class GetUserDepend(object):
        user_name: str = field.Query.i()
        age: int = field.Query.i()

        def __init__(self, age_limit: int = 18) -> None:
            self.age_limit: int = age_limit

        def __call__(self, token: str = field.Header.i()) -> str:
            if token not in fake_db_dict:
                raise RuntimeError(f"Can not found by token:{token}")
            user_name = fake_db_dict[token]
            if user_name != self.user_name:
                raise RuntimeError("The specified user could not be found through the token")
            if self.age < self.age_limit:
                raise ValueError("Minors cannot access")
            return user_name


    @pait()
    def demo(user_name: str = field.Depends.i(partial_wrapper(GetUserDepend, age_limit=16))):
        pass

    @pait()
    def demo1(user_name: str = field.Depends.i(GetUserDepend)):
        pass
    ```
    In this example,
    each route function has different age restrictions for users.
    Among them, `demo` restricts access to users younger than 16 years old,
    while `demo1` restricts access to users younger than 18 years old.
    So their initialization parameters of `GetUserDepend` are different.

    To that end, the `demo` function uses `pait.util.partial_wrapper` to bind the initialization parameters to `GetUserDepend`.
    The function of `pait.util.partial_wrapper` is similar to the official `functools.partial`.
    The only difference is that it supports PEP 612, can get code tips and use inspection tools for code inspection.


## 4.Pre-Depend
In some scenarios,
the route function only needs the `Depends` function to perform verification logic and does not need the return value of the `Depends` function.
At this time, may consider using the variable name `_` instead, as follows:
```python
@pait()
def demo(_: str = field.Depends.i(get_user_by_token)) -> None:
    pass
```
However, `Python` does not support multiple variables with the same name in a function,
which means that when there are multiple similar parameters, their variable names cannot be changed to `_`.

For this reason, `Pait` solves this problem through the optional parameter `pre_depend_list`.
Its use is very simple, only need to migrate the `Depend` function from the parameters to the `pre_depend_list` optional parameters of `Pait`.
Neither the logic nor the functionality of the `Depend` code will be affected, and the modified code will look like the following (the highlighted code is the modified part):

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"  hl_lines="23-24"

    --8<-- "docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"   hl_lines="26-27"
    --8<-- "docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"   hl_lines="23-24"
    --8<-- "docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"    hl_lines="29-20"
    --8<-- "docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"
    ```

After running the code and executing the `curl` command, can see that `Pre-Depend` can work normally through the following output.:
<!-- termynal -->
```python
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"msg":"success"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```


!!! note
    - 1.When using `Pre-Depend`, `Pait` will first execute `Pre-Depend` in sequence and then execute the route function. If there is an error in the execution of `Pre-Depend`, an error will be thrown directly.
    - 2.`Pre-Depend` is bound to `Pait` instead of a route function, which means that `Pre-Depend` can be reused together with `Pait`, see for details [Reuse of Pait](/2_how_to_use_pait/)。


## 5.:warning:Don't share limited resources
`Depend` is the best implementation for sharing the same logic, it is important to be careful not to share limited resources,
Because the shared resources are for the entire route function, which means that it may affect the concurrency count of the system, or even bring down the entire system.

!!! note
    There are many types of finite resources, common finite resources are: thread pools, `MySQL` connection pools, `Redis` connection pools, etc.

Since the content of this section has nothing to do with the use of `Pait`, the dangers of sharing limited resources will be illustrated by using the `Redis` connection as an example.

!!! note
    - 1.The best demonstration use case is the connection pool of `MySQL`, but in order to save the amount of code, the `Redis` connection is used here to briefly explain the dangers of sharing limited resources.
    - 2.Normally, you don't get a connection to `Redis` directly, and `Redis` doesn't expose a similar interface. It's just that the execution logic of the `execute_command` method is similar to getting a connection, so we'll use it as an example.


A `Redis` connection can only do one thing,
but `Redis` itself is so well designed that clients can still achieve high concurrency with connection pooling.
However, if the logic of the route function is complex and takes a long time to execute,
then the concurrency of the entire service is limited by the number of connection pools, as in the following code.
```Python
import time
from typing import Callable
from flask import Flask, Response, jsonify
from redis import Redis
from pait.app.flask import pait
from pait import field

redis = Redis(max_connections=100)


def get_redis() -> Callable:
    return redis.execute_command


@pait()
def demo(my_redis_conn: Callable = field.Depends.i(get_redis)) -> Response:
    # mock redis cli
    my_redis_conn("info")
    # mock io
    time.sleep(5)
    return jsonify()


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.run(port=8000)
```
Each route function in the sample code will first obtain the `Redis` connection,
then execute the route function logic and finally release the `Redis` connection.
Therefore, the usage time of `Redis` connection is the running time of the entire route function,
which means that if the logic of the route function is relatively complex,
the number of concurrency of the entire service will be limited by the number of `Redis` connection pool.
Just like the `demo` route function in the example code,
the `demo` route function will first call `Redis`'s `info` command and then simulate an `IO` operation sleeping for 5 seconds.
This means that after getting the `Redis` connection,
most of the time of the `Redis` connection is wasted waiting for the `IO` operation, which is very bad.

To solve this problem is very simple, just change the shared resources into a shared method of obtaining resources, as shown in the following code:
```py linenums="1" hl_lines="12 18-20"
import time
from typing import Callable
from flask import Flask, Response, jsonify
from redis import Redis
from pait.app.flask import pait
from pait import field

redis = Redis(max_connections=100)


def get_redis() -> Callable:
    return lambda :redis.execute_command


@pait()
def demo(my_redis_conn: Callable = field.Depends.i(get_redis)) -> Response:
    # mock redis cli
    conn = my_redis_conn()
    conn("info")
    del conn
    # mock io
    time.sleep(5)
    return jsonify()


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.run(port=8000)
```
There are two parts of this code that have changed.
The first part is the first highlighted code,
which changes the `get_redis` function from returning a `Redis` connection to returning a method to get a `Redis` connection.
The second part is the second highlighted code,
which changes from calling the `Redis` connection directly to first getting the `Redis` connection and then calling it and finally releasing the `Redis` connection.

In this way, the connection to `Redis` will only be obtained when `Redis` is used,
and the concurrency of the system will not be easily affected by the `Redis` connection pool.
