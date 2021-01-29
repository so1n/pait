# Pait Doc
<details><summary>Group: root</summary>

### Name: test_raise_tip

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#DC143C>abandoned</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 27">test_raise_tip</abbr>|test pait raise tip|
- Path: /api/raise_tip
- Method: POST
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |content_type|string|**`Required`**|content-type|{}|
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
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
            |data.uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type|{}|
            |data.test.test_a|integer|**`Required`**||{}|
            |data.test.test_b|string|**`Required`**||{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

### Name: test_pait_model

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#00BFFF>test</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 112">test_pait_model</abbr>|Test Field|
- Path: /api/pait_model
- Method: GET,HEAD
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|**`Required`**|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

</details><details><summary>Group: user</summary>

### Name: test_post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 46">test_post</abbr>|Test Method:Post Pydantic Model|
- Path: /api/post
- Method: POST
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |Content-Type|string|**`Required`**|content-type|{}|
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
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
            |data.uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type|{}|
            |data.test.test_a|integer|**`Required`**||{}|
            |data.test.test_b|string|**`Required`**||{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

### Name: test_depend

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 65">test_depend</abbr>|Test Method:Post request, Pydantic Model|
- Path: /api/depend
- Method: GET,HEAD
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|user agent|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
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
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
            |data.uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
            |data.user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
            |data.age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
            |data.content_type|string|**`Required`**|content-type|{}|
            |data.test.test_a|integer|**`Required`**||{}|
            |data.test.test_b|string|**`Required`**||{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

### Name: test_get

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 87">test_get</abbr>|Test Field|
- Path: /api/get/{age}
- Method: GET,HEAD
- Request:
    - Path

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|string|**`Required`**|age|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |sex|enum|Only choose from: `man`,`woman`|sex|{'enum': ['man', 'woman']}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

### Name: TestCbv.get

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 126">TestCbv.get</abbr>|Text Pydantic Model and Field|
- Path: /api/cbv
- Method: get
- Request:
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua|{}|
    - Query

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
        |email|string|example@xxx.com|user email|{}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

### Name: TestCbv.post

|Author|Status|func|description|
|---|---|---|---|
|so1n|<font color=#32CD32>release</font>|<abbr title="file:/home/so1n/github/pait/example/param_verify/starlette_example.py;line: 150">TestCbv.post</abbr>|test cbv post method|
- Path: /api/cbv
- Method: post
- Request:
    - Body

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |uid|integer|123456|user id|{'exclusiveMinimum': 10, 'exclusiveMaximum': 1000}|
        |user_name|string|**`Required`**|user name|{'minLength': 2, 'maxLength': 4}|
        |age|integer|**`Required`**|age|{'exclusiveMinimum': 1, 'exclusiveMaximum': 100}|
    - Header

        |param name|type|default value|description|other|
        |---|---|---|---|---|
        |user-agent|string|**`Required`**|ua|{}|
- Response:

    - SuccessRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|success response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|0|api code|{}|
            |msg|string|success|api status msg|{}|
    - FailRespModel

        |status code|media type|description|
        |---|---|---|
        |200|application/json|fail response|
        - Data

            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |code|integer|1|api code|{}|
            |msg|string|fail|api status msg|{}|

</details>