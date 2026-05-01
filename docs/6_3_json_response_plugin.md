Currently the most used serialization method in the route function is JSON,
so `Pait` also comes with some JSON response related plug-ins, such as checking the JSON response result,
automatically replenishing the JSON response result data, etc.,
which all use the `response model_list` in the response model to expand the corresponding functions.


!!! note
    - 1.Since the plugin needs to get the returned results, the plugin may intrude into the web framework, resulting in a somewhat different usage than the original usage.
    - 2.Plugins need to be adapted to different web frameworks, so please introduce the corresponding plugin in the form of `from pait.app.{web framework name}.plugin.{plugin name} import xxx`.

## Check the JSON response result plugin
The `CheckJsonPlugin` plugin is mainly used to check the response result of the route function, if the check is successful,
the response will be returned, otherwise an error will be thrown, as shown below:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/flask_with_check_json_plugin_demo.py"

    --8<-- "docs_source_code/plugin/json_plugin/flask_with_check_json_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/starlette_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/starlette_with_check_json_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/sanic_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/sanic_with_check_json_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/tornado_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/tornado_with_check_json_plugin_demo.py"
    ```
The first step is to define a JSON response result model called `UserSuccessRespModel3`.
Then define an error handler function that catches exceptions thrown when the plugin fails to validate the results.
Next is to define a `demo` route function that uses the `CheckJsonRespPlugin` plugin.
Also, when `display_age` is not equal to 1,
the result returned by the `demo` route function will not match the `UserSuccessRespModel3`.

After running the code and executing the following commands,
can find through the execution results that when the response result does not match the defined response Model,
an error will be thrown directly:
```bash
➜  curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code": 0, "msg": "", "data": {"uid": 123, "user_name": "so1n", "email": "example@xxx.com", "age": 18}}
➜  curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18
1 validation error for ResponseModel
data -> age
  field required (type=value_error.missing)
```


## Autocomplete JSON response result plugin
The result returned by the route function should be consistent with the structure defined in the API documentation,
because returning only some of the fields may cause the client to crash.
If for some reason only part of the structure can be returned,
then can use the AutoComplete JSON Response plugin to fill in the default values for the fields that are missing,
as in the following example:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/flask_with_auto_complete_json_plugin_demo.py"

    --8<-- "docs_source_code/plugin/json_plugin/flask_with_auto_complete_json_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/starlette_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/starlette_with_auto_complete_json_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/sanic_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/sanic_with_auto_complete_json_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/json_plugin/tornado_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/plugin/json_plugin/tornado_with_auto_complete_json_plugin_demo.py"
    ```

First define an `AutoCompleteRespModel` response Model with a default value of 100 for the `UID` in the Model.
Then create a `demo` function, which has some fields missing from the return structure,
but uses the `AutoCompleteJsonRespPlugin` plugin.

Run the code and execute the following command:
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{
  "code":0,
  "data":{
      "image_list":[{},{}],
      "music_list":[{"name":"music1","singer":"singer1","url":"http://music1.com"},{"name":"","singer":"","url":"http://music1.com"}],
      "uid":100
    },
  "msg":""
}
```
The output shows that `data->uid`, `data->music_list->[0]->name` and `data->music_list->[0]->singer` have been supplemented with default values.
The default value of `data->uid` is defined for the Field of `AutoCompleteRespModel`,
while the default values of the other fields are zero values corresponding to the type.


!!! note
    1.The default value of the response can be defined through `default` or `default_factory` of `Field`.
    2.AutoCompletePlugin intrudes into the routing function, causing the routing function to return only `Python` types instead of response objects.
