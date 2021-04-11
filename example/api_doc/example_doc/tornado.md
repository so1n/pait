# Pait Doc
<details><summary>Group: root</summary>

### Name: RaiseTipHandler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 34">RaiseTipHandler.post</abbr>|test pait raise tip|
- Path: /api/raise_tip$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content_type|string|**`Required`**|content-type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


### Name: TestPaitModelHanler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 147">TestPaitModelHanler.post</abbr>|Test Field|
- Path: /api/pait_model$
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
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


</details><details><summary>Group: user</summary>

### Name: TestPostHandler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 55">TestPostHandler.post</abbr>|Test Method:Post Pydantic Model|
- Path: /api/post$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|content-type||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


### Name: TestDependHandler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 76">TestDependHandler.post</abbr>|Test Method:Post request, Pydantic Model|
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
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


### Name: TestGetHandler.get

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 97">TestGetHandler.get</abbr>|Test Field|
- Path: /api/get/(?P<age>\w+)$
- Method: get
- Request:
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
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|user email||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "email": "",
                "age": 0
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


### Name: TestOtherFieldHandler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 118">TestOtherFieldHandler.post</abbr>||
- Path: /api/other_field$
- Method: post
- Request:
    - Cookie Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |cookie|object|**`Required`**|cookie||
    - File Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |upload_file|PydanticUndefined|**`Required`**|upload file||
    - Form Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |a|string|**`Required`**|form data||
        |b|string|**`Required`**|form data||
- Response:


### Name: TestCbvHandler.get

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 161">TestCbvHandler.get</abbr>|Text Pydantic Model and Field|
- Path: /api/cbv$
- Method: get
- Request:
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua||
    - Query Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |email|string|example@xxx.com|user email||
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
- Response:

    - UserSuccessRespModel2

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.email|string|**`Required`**|user email||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "email": "",
                "age": 0
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


### Name: TestCbvHandler.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 179">TestCbvHandler.post</abbr>|test cbv post method|
- Path: /api/cbv$
- Method: post
- Request:
    - Body Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
    - Header Param

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua||
- Response:

    - UserSuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Header
            {'cookie': 'xxx'}
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code||
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type||
            |data.uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'maxLength': 4, 'minLength': 2}|
            |msg|string|success|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": "",
              "data": {
                "uid": 0,
                "user_name": "",
                "age": 0,
                "content_type": ""
              }
            }
            ```

    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code||
            |msg|string|fail|api status msg||
        - Example Response Data Json

            ```json
            {
              "code": 0,
              "msg": ""
            }
            ```


</details>