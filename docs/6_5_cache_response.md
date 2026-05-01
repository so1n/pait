The Cache plugin can cache any response object other than streaming responses based on different request parameters.
It can be used as follows.
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/flask_with_cache_plugin_demo.py"

    --8<-- "docs_source_code/plugin/cache_plugin/flask_with_cache_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/starlette_with_cache_plugin_demo.py"
    --8<-- "docs_source_code/plugin/cache_plugin/starlette_with_cache_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/sanic_with_cache_plugin_demo.py"
    --8<-- "docs_source_code/plugin/cache_plugin/sanic_with_cache_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/tornado_with_cache_plugin_demo.py"
    --8<-- "docs_source_code/plugin/cache_plugin/tornado_with_cache_plugin_demo.py"
    ```
The route function uses a `CachePlugin` that declares a cache time of 10 seconds and enables the cache name to include the request parameters.
Also, only the `key1` parameter in the route function uses the `CacheRespExtraParam` expansion parameter,
so that the `CachePlugin` will only take the parameter that uses the `CacheRespExtraParam` parameter, not all of them.

After running the code and executing the `curl` command,
can see that the route function returns the same content when the request parameters are the same:
<!-- termynal -->
```bash
> curl http://127.0.0.1:8000/api/demo\?key1\=1\&key2\=1
1695627610.021101
> curl http://127.0.0.1:8000/api/demo\?key1\=1\&key2\=1
1695627610.021101
> curl http://127.0.0.1:8000/api/demo\?key1\=2\&key2\=1
1695627613.0265439
```


In addition to the `cache_time` and `enable_cache_name_merge_param` parameters, `CachePlugin` supports other parameters, as described below:

- redis: Specify the Redis instance used by the cache plugin, it is recommended to specify the Redis instance via the `CacheResponsePlugin.set_redis_to_app` method.
- name: Specify the cache Key of the route function, if this value is null, the cache Key is the name of the route function.
- enable_cache_name_merge_param: If True, the construction of the cached Key will include other parameter values, such as the following route function.
    ```Python
    from pait.app.any import pait
    from pait.plugin.cache_response import CacheResponsePlugin
    from pait.field import Query

    @pait(post_plugin_list=[CacheResponsePlugin.build(cache_time=10)])
    async def demo(uid: str = Query.i(), name: str = Query.i()) -> None:
        pass
    ```
    When the request url carries `?uid=10086&name=so1n`, the cache plugin generates a cache Key of `demo:10086:so1n`.
    However, if the parameter `uid` uses the `CacheRespExtraParam` expansion parameter, then the cached Key will only include the value of the parameter that uses the `CacheRespExtraParam` expansion parameter, such as the following route function:
    ```Python
    from pait.app.any import pait
    from pait.plugin.cache_response import CacheResponsePlugin, CacheRespExtraParam
    from pait.field import Query

    @pait(post_plugin_list=[CacheResponsePlugin.build(cache_time=10)])
    async def demo(uid: str = Query.i(extra_param_list=[CacheRespExtraParam()]), name: str = Query.i()) -> None:
        pass
    ```
    When the request url carries `?uid=10086&name=so1n`, the cache plugin generates a cache Key of `demo:10086`.
- include_exc: Receive a Tuple that can be exception, if the error thrown by the route function belongs to one of the errors in the Tuple, the exception will be cached, otherwise the exception will be thrown.
- cache_time: cache time in seconds.
- timeout: To prevent cache conflicts in highly concurrent scenarios, the cache plugin uses `Reids` locks to prevent resource contention. timeout represents the maximum time the lock can be held.
- sleep: When a lock is found to be held by another request, the current request will sleep for a specified amount of time before attempting to acquire the lock, and so on until it acquires the corresponding lock or times out.
- blocking_timeout: the maximum time to try to acquire the lock, if None, it will wait forever.
