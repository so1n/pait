In the development process,
the back-end developer will often define the API document and discuss the implementation of the API with the front-end developer through the API document and make modifications,
there is no specific implementation of the API in this stage.
In this stage, the front-end and back-end developers will be developed at the same time,
then there may be a front-end developers need to debug the API in the development process,
but due to the back-end developers have not yet completed the development of the front-end developers can not be debugging the situation.

To do this, the `Mock` plugin can be used to return the specified response data for route functions that do not implement the logic, as follows:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py"

    --8<-- "docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py"
    ```

The code first implements a response object called `UserSuccessRespModel2`, which differs from the previous response object in that some of its fields have `example` attributes.
Then it creates a `demo` route function without any code logic, which has only a few parameters and uses the `Mock` plugin and the `UserSuccessRespModel2` response object via `pait`.

Run the code and execute the following command, the output shows that after using the `Mock` plugin,
the route function is able to return data and the data is the same as the value of `example` in the `UserSuccessRespModel2` response object:
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"code":0,"data":{"age":99,"email":"example@so1n.me","multi_user_name":["mock_name"],"uid":666,"user_name":"mock_name"},"msg":"success"}
```

!!! note
    - 1.example also supports factory functions, which have a similar effect to `default_factory`. Available values are `example=time.now`, `example=lambda :random.randint(100000, 900000)` and so on.
    - 2.Mock plugin supports defining the name of the field to be adopted by the parameter `example_column_name`, which is `example` by default and can also be `mock`.
