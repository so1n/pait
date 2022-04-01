# Pait Doc
<details><summary>组: check_resp</summary>

### 名称: TextResponseHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 407">TextResponseHanler.get</abbr>|    |
- 路径: /api/text-resp$
- 方法: get
- 请求:
- 响应:

    - TextRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|text/plain|text response|
        - Header
            {'X-Example-Type': 'text'}

### 名称: HtmlResponseHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 415">HtmlResponseHanler.get</abbr>|    |
- 路径: /api/html-resp$
- 方法: get
- 请求:
- 响应:

    - HtmlRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|text/html|html response|
        - Header
            {'X-Example-Type': 'html'}

### 名称: FileResponseHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 423">FileResponseHanler.get</abbr>|    |
- 路径: /api/file-resp$
- 方法: get
- 请求:
- 响应:

    - FileRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/octet-stream|file response|
        - Header
            {'X-Example-Type': 'file'}

</details><details><summary>组: links</summary>

### 名称: LoginHanlder.post

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 436">LoginHanlder.post</abbr>|    |
- 路径: /api/login$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |password|string|**`必填`**| |password||
        |uid|string|**`必填`**| |user id||
- 响应:

    - LoginRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|login response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.token|string|**`必填`**| | ||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {
                "token": ""
              }
            }
            ```


### 名称: GetUserHandler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 449">GetUserHandler.get</abbr>|    |
- 路径: /api/user$
- 方法: get
- 请求:
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |token|string| | |token||
- 响应:

    - SuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```


</details><details><summary>组: other</summary>

### 名称: ~~RaiseTipHandler.post~~



**描述**:test pait raise tip

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#DC143C>abandoned</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 81">RaiseTipHandler.post</abbr>|    |
- 路径: /api/raise-tip$
- 方法: post
- 请求:
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |content__type|string|**`必填`**| |content-type||
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: DependHandler.post



**描述**:Test Method:Post request, Pydantic Model

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 117">DependHandler.post</abbr>|    |
- 路径: /api/depend$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |user-agent|string|**`必填`**| |user agent||
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: SameAliasHandler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 133">SameAliasHandler.get</abbr>|    |
- 路径: /api/same-alias$
- 方法: get
- 请求:
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |token|string| | | ||
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |token|string| | | ||
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: PaitModelHanler.post



**描述**:Test pait model

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 304">PaitModelHanler.post</abbr>|    |
- 路径: /api/pait-model$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |user_info|object|**`必填`**| | |[`properties:{'user_name': {'title': 'User Name', 'description': 'user name', 'maxLength': 4, 'minLength': 2, 'type': 'string'}, 'age': {'title': 'Age', 'description': 'age', 'exclusiveMinimum': 1, 'exclusiveMaximum': 100, 'type': 'integer'}}`], [`required:['user_name', 'age']`]|
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |user-agent|string|**`必填`**| |user agent||
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: DependContextmanagerHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 311">DependContextmanagerHanler.get</abbr>|    |
- 路径: /api/check-depend-contextmanager$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- 响应:

    - SuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: DependAsyncContextmanagerHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 319">DependAsyncContextmanagerHanler.get</abbr>|    |
- 路径: /api/check-depend-async-contextmanager$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- 响应:

    - SuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: PreDependContextmanagerHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 327">PreDependContextmanagerHanler.get</abbr>|    |
- 路径: /api/check-pre-depend-contextmanager$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- 响应:

    - SuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: PreDependAsyncContextmanagerHanler.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 337">PreDependAsyncContextmanagerHanler.get</abbr>|    |
- 路径: /api/check-pre-depend-async-contextmanager$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |is_raise|boolean| | | ||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
- 响应:

    - SuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success"
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details><details><summary>组: pait_doc</summary>

### 名称: GetRedocHtmlHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 54">AddDocRoute._gen_route.<locals>.GetRedocHtmlHandle.get</abbr>|    |
- 路径: /api-doc/redoc$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


### 名称: GetSwaggerUiHtmlHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 59">AddDocRoute._gen_route.<locals>.GetSwaggerUiHtmlHandle.get</abbr>|    |
- 路径: /api-doc/swagger$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


### 名称: OpenApiHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 64">AddDocRoute._gen_route.<locals>.OpenApiHandle.get</abbr>|    |
- 路径: /api-doc/openapi.json$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


### 名称: GetRedocHtmlHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 54">AddDocRoute._gen_route.<locals>.GetRedocHtmlHandle.get</abbr>|    |
- 路径: /redoc$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


### 名称: GetSwaggerUiHtmlHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 59">AddDocRoute._gen_route.<locals>.GetSwaggerUiHtmlHandle.get</abbr>|    |
- 路径: /swagger$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


### 名称: OpenApiHandle.get

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |    |undefined    |<abbr title="file:/home/so1n/github/pait/pait/app/tornado/_route.py;line: 64">AddDocRoute._gen_route.<locals>.OpenApiHandle.get</abbr>|    |
- 路径: /openapi.json$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |pin_code|string| | | ||
- 响应:


</details><details><summary>组: plugin</summary>

### 名称: AutoCompleteJsonHandler.get



**描述**:Test json plugin by resp type is dict

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 458">AutoCompleteJsonHandler.get</abbr>|    |
- 路径: /api/auto-complete-json-plugin$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel3

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**| |user email||
            |data.uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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


### 名称: CheckJsonPluginHandler.get



**描述**:Test json plugin by resp type is dict

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 483">CheckJsonPluginHandler.get</abbr>|    |
- 路径: /api/check-json-plugin$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel3

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**| |user email||
            |data.uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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


### 名称: CheckJsonPlugin1Handler.get



**描述**:Test json plugin by resp type is typed dict

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |undefined    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 526">CheckJsonPlugin1Handler.get</abbr>|    |
- 路径: /api/check-json-plugin-1$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel3

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**| |user email||
            |data.uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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


</details><details><summary>组: user</summary>

### 名称: PostHandler.post



**描述**:Test Method:Post Pydantic Model

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 96">PostHandler.post</abbr>|    |
- 路径: /api/post$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**|123|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**|so1n|user name|[`maxLength:4`], [`minLength:2`]|
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |Content-Type|string|**`必填`**| |content-type||
- 响应:

    - UserSuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`必填`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: FieldDefaultFactoryHandler.post

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#00BFFF>test</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 145">FieldDefaultFactoryHandler.post</abbr>|    |
- 路径: /api/field-default-factory$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |data_dict|object|**`必填`**| |test default factory||
        |data_list|array|**`必填`**| |test default factory|[`items:{'type': 'string'}`]|
        |demo_value|integer|**`必填`**| |Json body value not empty||
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: PaitBaseFieldHandler.post

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 162">PaitBaseFieldHandler.post</abbr>|    |
- 路径: /api/pait-base-field/(?P<age>\w+)$
- 方法: post
- 请求:
    - Cookie 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |cookie|object|**`必填`**| |cookie||
    - File 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |upload_file|object|**`必填`**| |upload file||
    - Form 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |a|string|**`必填`**| |form data||
        |b|string|**`必填`**| |form data||
    - Multiform 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |c|array|**`必填`**| |form data|[`items:{'type': 'string'}`]|
    - Multiquery 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - SimpleRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data|object|**`必填`**| |success result||
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 0,
              "msg": "success",
              "data": {}
            }
            ```

    - FailRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: MockHandler.get



**描述**:Test Field

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 270">MockHandler.get</abbr>|    |
- 路径: /api/mock/(?P<age>\w+)$
- 方法: get
- 请求:
    - Multiquery 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |multi_user_name|array|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 4}`]|
    - Path 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age||
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel2

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**|99|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**|example@so1n.me|user email||
            |data.multi_user_name|array|**`必填`**|['mock_name']|user name|[`maxLength:10`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 10}`]|
            |data.uid|integer|**`必填`**|666|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**|mock_name|user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: CbvHandler.get



**描述**:Text Pydantic Model and Field

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 351">CbvHandler.get</abbr>|    |
- 路径: /api/cbv$
- 方法: get
- 请求:
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |Content-Type|string|**`必填`**| | ||
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`必填`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: CbvHandler.post



**描述**:test cbv post method

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 378">CbvHandler.post</abbr>|    |
- 路径: /api/cbv$
- 方法: post
- 请求:
    - Body 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**|25|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
    - Header 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |Content-Type|string|**`必填`**| | ||
- 响应:

    - UserSuccessRespModel

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|99| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.content_type|string|**`必填`**| |content-type||
            |data.uid|integer|666| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|mock_name| |user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: CheckParamHandler.get



**描述**:Test check param

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 204">CheckParamHandler.get</abbr>|    |
- 路径: /api/check-param$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |alias_user_name|string| | |user name|[`maxLength:4`], [`minLength:2`]|
        |birthday|string| | |birthday||
        |email|string|example@xxx.com| |user email||
        |sex|enum|Only choose from: `man`,`woman`| |sex|[`enum:['man', 'woman']`]|
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string| | |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel2

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**|99|age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**|example@so1n.me|user email||
            |data.multi_user_name|array|**`必填`**|['mock_name']|user name|[`maxLength:10`], [`minLength:2`], [`items:{'type': 'string', 'minLength': 2, 'maxLength': 10}`]|
            |data.uid|integer|**`必填`**|666|user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**|mock_name|user name|[`maxLength:10`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


### 名称: CheckRespHandler.get



**描述**:Test test-helper check response

- API 信息

    |作者|状态|函数|摘要|
    |---|---|---|---|
    |so1n    |<font color=#32CD32>release</font>    |<abbr title="file:/home/so1n/github/pait/example/param_verify/tornado_example.py;line: 241">CheckRespHandler.get</abbr>|    |
- 路径: /api/check-resp$
- 方法: get
- 请求:
    - Query 参数

        |参数 名称|类型|默认|示例|描述|其它|
        |---|---|---|---|---|---|
        |age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
        |display_age|integer| | |display_age||
        |email|string|example@xxx.com| |user email||
        |uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
        |user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
- 响应:

    - UserSuccessRespModel3

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|success response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer| | |api code||
            |data.age|integer|**`必填`**| |age|[`exclusiveMinimum:1`], [`exclusiveMaximum:100`]|
            |data.email|string|**`必填`**| |user email||
            |data.uid|integer|**`必填`**| |user id|[`exclusiveMinimum:10`], [`exclusiveMaximum:1000`]|
            |data.user_name|string|**`必填`**| |user name|[`maxLength:4`], [`minLength:2`]|
            |msg|string|success| |api status msg||
        - 示例 响应 Json 数据

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

        - 响应 信息

            |状态 码|媒体 类型|描述|
            |---|---|---|
            |200|application/json|fail response|
        - 响应 数据

            |参数 名称|类型|默认|示例|描述|其它|
            |---|---|---|---|---|---|
            |code|integer|1| |api code||
            |msg|string|fail| |api status msg||
        - 示例 响应 Json 数据

            ```json
            {
              "code": 1,
              "msg": "fail"
            }
            ```


</details>