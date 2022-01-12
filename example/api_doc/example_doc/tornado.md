# Pait Doc
<details><summary>Group: check_resp</summary>

### Name: TextResponseHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 393">TextResponseHanler.get</abbr>|    |
- Path: /api/text-resp$
- Method: get
- Request:
- Response:

    - TextRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### Name: HtmlResponseHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 401">HtmlResponseHanler.get</abbr>|    |
- Path: /api/html-resp$
- Method: get
- Request:
- Response:

    - HtmlRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### Name: FileResponseHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 409">FileResponseHanler.get</abbr>|    |
- Path: /api/file-resp$
- Method: get
- Request:
- Response:

    - FileRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>Group: links</summary>

### Name: LoginHanlder.post

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 422">LoginHanlder.post</abbr>|    |
- Path: /api/login$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |password|string|**`Required`**| |password| |
        |uid|string|**`Required`**| |user id| |
- Response:

    - LoginRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|login response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.token|string|**`Required`**| | | |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "token": ""
              }
            }
            ```


### Name: GetUserHandler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 435">GetUserHandler.get</abbr>|    |
- Path: /api/user$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | |token| |
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```


</details><details><summary>Group: other</summary>

### Name: ~~RaiseTipHandler.post~~



**Desc**:test pait raise tip

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#DC143C>abandoned</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 67">RaiseTipHandler.post</abbr>|    |
- Path: /api/raise-tip$
- Method: post
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |content_type|string|**`Required`**| |content-type| |
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependHandler.post



**Desc**:Test Method:Post request, Pydantic Model

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 103">DependHandler.post</abbr>|    |
- Path: /api/depend$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent| |
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: SameAliasHandler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 119">SameAliasHandler.get</abbr>|    |
- Path: /api/same-alias$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | | | |
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |token|string| | | | |
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PaitModelHanler.post



**Desc**:Test pait model

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 290">PaitModelHanler.post</abbr>|    |
- Path: /api/pait-model$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user_info|object|**`Required`**| | |{'properties': {'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}, 'required': ['user_name', 'age']}|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |user-agent|string|**`Required`**| |user agent| |
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependContextmanagerHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 297">DependContextmanagerHanler.get</abbr>|    |
- Path: /api/check-depend-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | | |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependAsyncContextmanagerHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 305">DependAsyncContextmanagerHanler.get</abbr>|    |
- Path: /api/check-depend-async-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | | |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PreDependContextmanagerHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 313">PreDependContextmanagerHanler.get</abbr>|    |
- Path: /api/check-pre-depend-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | | |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PreDependAsyncContextmanagerHanler.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 323">PreDependAsyncContextmanagerHanler.get</abbr>|    |
- Path: /api/check-pre-depend-async-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | | |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details><details><summary>Group: pait_doc</summary>

### Name: GetRedocHtmlHandle.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 71">add_doc_route.<locals>.GetRedocHtmlHandle.get</abbr>|    |
- Path: /redoc$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | | |
- Response:


### Name: GetSwaggerUiHtmlHandle.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 76">add_doc_route.<locals>.GetSwaggerUiHtmlHandle.get</abbr>|    |
- Path: /swagger$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | | |
- Response:


### Name: OpenApiHandle.get

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 81">add_doc_route.<locals>.OpenApiHandle.get</abbr>|    |
- Path: /openapi.json$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |pin_code|string| | | | |
- Response:


</details><details><summary>Group: plugin</summary>

### Name: CheckJsonPluginHandler.get



**Desc**:Test json plugin by resp type is dict

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 444">CheckJsonPluginHandler.get</abbr>|    |
- Path: /api/check-json-plugin$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |display_age|integer| | |display_age| |
        |email|string|example@xxx.com| |user email| |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**| |user email| |
            |data.uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```


### Name: CheckJsonPlugin1Handler.get



**Desc**:Test json plugin by resp type is typed dict

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 487">CheckJsonPlugin1Handler.get</abbr>|    |
- Path: /api/check-json-plugin-1$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |display_age|integer| | |display_age| |
        |email|string|example@xxx.com| |user email| |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**| |user email| |
            |data.uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```


</details><details><summary>Group: user</summary>

### Name: PostHandler.post



**Desc**:Test Method:Post Pydantic Model

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 82">PostHandler.post</abbr>|    |
- Path: /api/post$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|123|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|so1n|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| |content-type| |
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|99| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**| |content-type| |
            |data.uid|integer|666| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name| |user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: FieldDefaultFactoryHandler.post

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 131">FieldDefaultFactoryHandler.post</abbr>|    |
- Path: /api/field-default-factory$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |data_dict|object|**`Required`**| |test default factory| |
        |data_list|array|**`Required`**| |test default factory|{'items': {'type': 'string'}}|
        |demo_value|integer|**`Required`**| |Json body value not empty| |
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PaitBaseFieldHandler.post

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 148">PaitBaseFieldHandler.post</abbr>|    |
- Path: /api/pait-base-field/(?P<age>\w+)$
- Method: post
- Request:
    - Cookie Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |cookie|object|**`Required`**| |cookie| |
    - File Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |upload_file|object|**`Required`**| |upload file| |
    - Form Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |a|string|**`Required`**| |form data| |
        |b|string|**`Required`**| |form data| |
    - Multiform Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |c|array|**`Required`**| |form data|{'items': {'type': 'string'}}|
    - Multiquery Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email| |
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - SimpleRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data|object|**`Required`**| |success result| |
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: MockHandler.get



**Desc**:Test Field

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 256">MockHandler.get</abbr>|    |
- Path: /api/mock/(?P<age>\w+)$
- Method: get
- Request:
    - Multiquery Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age| |
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email| |
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|**`Required`**|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|example@so1n.me|user email| |
            |data.multi_user_name|array|**`Required`**|('mock_name',)|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
                "age": 99,
                "email": "example@so1n.me"
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvHandler.get



**Desc**:Text Pydantic Model and Field

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 337">CbvHandler.get</abbr>|    |
- Path: /api/cbv$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | | |
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|99| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**| |content-type| |
            |data.uid|integer|666| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name| |user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvHandler.post



**Desc**:test cbv post method

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 364">CbvHandler.post</abbr>|    |
- Path: /api/cbv$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**|25|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |Content-Type|string|**`Required`**| | | |
- Response:

    - UserSuccessRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|99| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**| |content-type| |
            |data.uid|integer|666| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name| |user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "age": 99,
                "sex": "man",
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CheckParamHandler.get



**Desc**:Test check param

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 190">CheckParamHandler.get</abbr>|    |
- Path: /api/check-param$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |alias_user_name|string| | |user name|{'maxLength': 4, 'minLength': 2}|
        |birthday|string| | |birthday| |
        |email|string|example@xxx.com| |user email| |
        |sex|enum|Only choose from: `man`,`woman`| |sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string| | |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|**`Required`**|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|example@so1n.me|user email| |
            |data.multi_user_name|array|**`Required`**|('mock_name',)|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 666,
                "user_name": "mock_name",
                "multi_user_name": [],
                "sex": "man",
                "age": 99,
                "email": "example@so1n.me"
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CheckRespHandler.get



**Desc**:Test test-helper check response

- API Info

    |Author|Status|func|summary|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 227">CheckRespHandler.get</abbr>|    |
- Path: /api/check-resp$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|example|description|other|
        |---|---|---|---|---|---|
        |age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |display_age|integer| | |display_age| |
        |email|string|example@xxx.com| |user email| |
        |uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel3

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|success response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer| | |api code| |
            |data.age|integer|**`Required`**| |age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**| |user email| |
            |data.uid|integer|**`Required`**| |user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**| |user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "email": ""
              }
            }
            ```

    - FailRespModel

        - Response Info

            |status code|media type|description|
            |---|---|---|
            |200|application/json|fail response|
        - Response Data

            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |code|integer|1| |api code| |
            |msg|string|fail| |api status msg| |
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details>
