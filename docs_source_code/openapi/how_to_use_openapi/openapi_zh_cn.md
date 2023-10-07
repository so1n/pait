# AnyApi
### 名称: demo.demo
**标签**: default
- 路径: /api/demo
- 方法: get
- 请求:
    **query**

     |名称|默认|类型|描述|示例|其它|
     |---|---|---|---|---|---|
     |uid|`必填`|integer|user id||exclusiveMinimum:10;<br>exclusiveMaximum:1000|
     |age|`必填`|integer|age||exclusiveMinimum:0|
     |username|`必填`|string|user name||maxLength:4;<br>minLength:2|


- 响应
**描述**: demo json response
*Header*

    - 200:application/json; charset=utf-8
    **响应信息**

         |名称|默认|类型|描述|示例|其它|
         |---|---|---|---|---|---|
         |code|`必填`|integer|||minimum:0|
         |msg|`必填`|string||||
         |data|`必填`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **响应示例**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
**描述**: demo json response
*Header*

    - 201:application/json; charset=utf-8
    **响应信息**

         |名称|默认|类型|描述|示例|其它|
         |---|---|---|---|---|---|
         |code|`必填`|integer|||minimum:0|
         |msg|`必填`|string||||
         |data|`必填`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **响应示例**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
**描述**: demo json response
*Header*

    - 404:application/json; charset=utf-8
    **响应信息**

         |名称|默认|类型|描述|示例|其它|
         |---|---|---|---|---|---|
         |code|`必填`|integer|||minimum:0|
         |msg|`必填`|string||||
         |data|`必填`|array|||items:{'$ref': '#/components/schemas/UserModel'}|

        **响应示例**

        ```json
        {
            "code": 0,
            "msg": "",
            "data": {
                "name": "so1n",
                "uid": 0,
                "age": 0
            }
        }
        ```
