# Pait Doc
<details><summary>Group: check_resp</summary>

### Name: TextResponseHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 362">TextResponseHanler.get</abbr>||
- Path: /api/text-resp$
- Method: get
- Request:
- Response:

    - TextRespModel

        |status code|media type|description|
        |---|---|---|
        |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### Name: HtmlResponseHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 370">HtmlResponseHanler.get</abbr>||
- Path: /api/html-resp$
- Method: get
- Request:
- Response:

    - HtmlRespModel

        |status code|media type|description|
        |---|---|---|
        |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### Name: FileResponseHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 379">FileResponseHanler.get</abbr>||
- Path: /api/file-resp$
- Method: get
- Request:
- Response:

    - FileRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>Group: links</summary>

### Name: LoginHanlder.post

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 392">LoginHanlder.post</abbr>||
- Path: /api/login$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |password|string|**`Required`**|password||
        |uid|string|**`Required`**|user id||
- Response:

    - LoginRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|login response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.token|string|**`Required`**|||
            |msg|string|success|api status msg||
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

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 405">GetUserHandler.get</abbr>||
- Path: /api/user$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||token||
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```


</details><details><summary>Group: other</summary>

### Name: RaiseTipHandler.post



**Desc**:test pait raise tip

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 56">RaiseTipHandler.post</abbr>||
- Path: /api/raise-tip$
- Method: post
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content_type|string|**`Required`**|content-type||
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependHandler.post



**Desc**:Test Method:Post request, Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 92">DependHandler.post</abbr>||
- Path: /api/depend$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent||
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: SameAliasHandler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 108">SameAliasHandler.get</abbr>||
- Path: /api/same-alias$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||None||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |token|string||None||
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PaitModelHanler.post



**Desc**:Test pait model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 260">PaitModelHanler.post</abbr>||
- Path: /api/pait-model$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user_info|object|**`Required`**|None|{'properties': {'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}, 'required': ['user_name', 'age']}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependContextmanagerHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 267">DependContextmanagerHanler.get</abbr>||
- Path: /api/check-depend-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: DependAsyncContextmanagerHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 276">DependAsyncContextmanagerHanler.get</abbr>||
- Path: /api/check-depend-async-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PreDependContextmanagerHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 285">PreDependContextmanagerHanler.get</abbr>||
- Path: /api/check-pre-depend-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PreDependAsyncContextmanagerHanler.get

|Author|Status|func|summary|
|---|---|---|---|
|so1n|undefined|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 294">PreDependAsyncContextmanagerHanler.get</abbr>||
- Path: /api/check-pre-depend-async-contextmanager$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |is_raise|boolean|False|None||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details><details><summary>Group: root</summary>

### Name: GetRedocHtmlHandle.get

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 63">add_doc_route.<locals>.GetRedocHtmlHandle.get</abbr>||
- Path: /redoc$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


### Name: GetSwaggerUiHtmlHandle.get

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 68">add_doc_route.<locals>.GetSwaggerUiHtmlHandle.get</abbr>||
- Path: /swagger$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


### Name: OpenApiHandle.get

|Author|Status|func|summary|
|---|---|---|---|
||undefined|<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 73">add_doc_route.<locals>.OpenApiHandle.get</abbr>||
- Path: /openapi.json$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |pin_code|string||None||
- Response:


</details><details><summary>Group: user</summary>

### Name: PostHandler.post



**Desc**:Test Method:Post Pydantic Model

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 71">PostHandler.post</abbr>||
- Path: /api/post$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': '123'}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': 'so1n'}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|content-type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: PaitBaseFieldHandler.post

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 120">PaitBaseFieldHandler.post</abbr>||
- Path: /api/pait-base-field/(?P<age>\w+)$
- Method: post
- Request:
    - Cookie Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |cookie|object|**`Required`**|cookie||
    - File Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |upload_file|object|**`Required`**|upload file||
    - Form Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |a|string|**`Required`**|form data||
        |b|string|**`Required`**|form data||
    - Multiform Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |c|array|**`Required`**|form data|{'items': {'type': 'string'}}|
    - Multiquery Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - SimpleRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data|object|**`Required`**|success result||
            |msg|string|success|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: MockHandler.get



**Desc**:Test Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 226">MockHandler.get</abbr>||
- Path: /api/mock/(?P<age>\w+)$
- Method: get
- Request:
    - Multiquery Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
    - Path Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvHandler.get



**Desc**:Text Pydantic Model and Field

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 306">CbvHandler.get</abbr>||
- Path: /api/cbv$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|None||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CbvHandler.post



**Desc**:test cbv post method

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 333">CbvHandler.post</abbr>||
- Path: /api/cbv$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 25}|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|None||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|99|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|666|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|mock_name|user name|{'maxLength': 10, 'minLength': 2}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CheckParamHandler.get



**Desc**:Test check param

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 162">CheckParamHandler.get</abbr>||
- Path: /api/check-param$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |alias_user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
        |birthday|string|None|birthday||
        |email|string|example@xxx.com|user email||
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'example': 99}|
            |data.email|string|**`Required`**|user email|{'example': 'example@so1n.me'}|
            |data.multi_user_name|array|**`Required`**|user name|{'maxLength': 4, 'minLength': 2, 'example': ('mock_name',), 'items': {'type': 'string', 'minLength': 2, 'maxLength': 4}}|
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000, 'example': 666}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 10, 'minLength': 2, 'example': 'mock_name'}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### Name: CheckRespHandler.get



**Desc**:Test check param

|Author|Status|func|summary|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 197">CheckRespHandler.get</abbr>||
- Path: /api/check-resp$
- Method: get
- Request:
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |display_age|integer|0|display_age||
        |email|string|example@xxx.com|user email||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|None|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel3

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|user email||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
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

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Response Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Json Data

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details>
