`Pait` is based on `Pydantic` to perform parameter checking and type conversion for each parameter,
which cannot satisfy the need for multiple parameter dependency checking.
For this reason,
`Pait` provides two kinds of parameter dependency checking functions through post plugins `Required` and `AtMostOneOf`.

## 1.Required Plugin
In the creation of route functions, often encounter some parameter dependencies,
such as having a request parameter A, B, C,
which B and C are optional and the requirement that B exists, C also needs to exist, B does not exist, C can not exist.
At this point, you can use the `Required` plugin for parameter restriction, the following code:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_demo.py" hl_lines="17"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_demo.py" hl_lines="18"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_demo.py"
    ```

The parameter `uid` is a required parameter in the route function, while the parameters `user_name` and `email` are optional,
but a new validation rule is added when the `ReuiredPlugin` plugin is used.
This validation rule is defined by `required_dict`, which states that the parameter `email` must depend on a collection of parameters to exist,
and that collection has only one parameter -- `user_name`.
So the validation rule for `RequiredPlugin` is that the parameter `email` can only exist if the parameter `user_name` exists.

After using `curl` to send a request through the response results can be found,
if the request parameter is only `uid` can be returned normally, but the request parameter `user_name` is null,
the parameter `email` must be null, otherwise it will report an error.
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"data":"email requires param user_name, which if not none"}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":"aaa"}%
```

The `Required` plugin can pass dependency rules through the `build` method,
but it can also define rules through the `ExtraParam` extension parameter.
The `Required` plugin supports both `RequiredExtraParam` and `RequiredGroupExtraParam` extension parameter.
The following code is a use of `RequiredExtraParam`,
which generates a validation rule for `user_name` dependent on `email` via `extra_param_list=[RequiredExtraParam(main_column="email")`.
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_extra_param_demo.py" hl_lines="17 20"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_extra_param_demo.py" hl_lines="20 23"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_extra_param_demo.py" hl_lines="18 21"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_extra_param_demo.py" hl_lines="21 27"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_extra_param_demo.py"
    ```


Another extension parameter `RequiredGroupExtraParam` is to categorize the parameters by `group` and mark one of the parameters in this group as the main parameter by `is_main`,
so that all other parameters in the group will depend on the main parameter.
The following sample code categorizes `user_name` and `email` parameters into `my-group`,
and defines the `email` parameter as the main parameter of `my-group`,
so that the generated validation rules depend on the `user_name` parameter and the `email` parameter.
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_group_extra_param_demo.py" hl_lines="17 21 24"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_group_extra_param_demo.py" hl_lines="20 24 27"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_group_extra_param_demo.py" hl_lines="18 22 25"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_group_extra_param_demo.py" hl_lines="21 26 29"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_group_extra_param_demo.py"
    ```

## 2.AtMostOneOf Plugin
The main function of the `AtMostOneOf` plugin is to verify whether the parameters are mutually exclusive.
for example, if there are three parameters A, B and C and the B parameter is required to be mutually exclusive with the C parameter,
that if B exists, C cannot exist, and if C exists, B cannot exist.
This can use `AtMostOneOf` plugin configuration rules to achieve the function, the code is as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_demo.py" hl_lines="17"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_demo.py" hl_lines="18"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_demo.py"
    ```

In the sample code, `uid` is a required parameter, while `user_name` and `email` are optional parameters,
and after using the `AtMostOneOfPlugin` plugin a new validation rule will be added.
This validation rule is defined by the parameter `at_most_one_of_list`,
which indicates that the parameters `email` and `user_name` cannot exist at the same time.

After sending a request using `curl`, the response shows that an error is returned when both `email` and `user_name` are present,
but otherwise the response is returned normally.
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"uid":"123","user_name":null,"email":"aaa"}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"data":"requires at most one of param email or user_name"}%
```

In addition, the `AtMostOneOf` plugin also supports grouping parameters by `ExtraParam` and restricting them to not appearing at the same time,
using the following method:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="17 20 21"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="20 23 24"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="18 21 22"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="21 26 28"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```
In this code, the `user_name` and `email` parameters are grouped into `my-group` using `AtMostOneOfExtraParam`.
At runtime, the `AtMostOneOf` plugin verifies that both the `user_name` and `email` parameters exist,
and throws an error if both exist.
