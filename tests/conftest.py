import asyncio
from contextlib import contextmanager
from queue import Queue
from typing import TYPE_CHECKING, Any, Callable, Generator, List, Optional, Tuple, Union

import grpc

from example.example_grpc.server import create_app
from pait.app import sniffing
from pait.extra.config import apply_block_http_method_set
from pait.g import config
from pait.plugin.base import PluginManager

if TYPE_CHECKING:
    from pait.model.core import PaitCoreModel

config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])


@contextmanager
def enable_plugin(route_handler: Callable, *plugin_manager_list: PluginManager) -> Generator[None, None, None]:
    if not getattr(route_handler, "_pait_id", None):
        raise TypeError("route handler must pait func")

    pait_core_model: "PaitCoreModel" = getattr(route_handler, "pait_core_model")
    raw_plugin_manager_list: List["PluginManager"] = pait_core_model._plugin_manager_list

    plugin_list: List[PluginManager] = []
    post_plugin_list: List[PluginManager] = []
    for plugin_manager in plugin_manager_list:
        if plugin_manager.plugin_class.is_pre_core:
            plugin_list.append(plugin_manager)
        else:
            post_plugin_list.append(plugin_manager)
    try:
        pait_core_model.add_plugin(plugin_list, post_plugin_list)
        yield
    finally:
        pait_core_model._plugin_manager_list = raw_plugin_manager_list


GRPC_RESPONSE = Union[grpc.Call, grpc.Future]


class ClientCallDetailsType(grpc.ClientCallDetails):
    method: str
    timeout: Optional[float]
    metadata: Optional[List[Tuple[str, Union[str, bytes]]]]
    credentials: Optional[grpc.CallCredentials]
    wait_for_ready: Optional[bool]
    compression: Optional[grpc.Compression]


class GrpcClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, queue: Queue):
        self.queue: Queue = queue

    def intercept_unary_unary(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request: Any,
    ) -> GRPC_RESPONSE:
        self.queue.put(request)
        return continuation(call_details, request)


class AioGrpcClientInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    def __init__(self, queue: Queue):
        self.queue: Queue = queue

    def intercept_unary_unary(
        self,
        continuation: Callable,
        call_details: ClientCallDetailsType,
        request: Any,
    ) -> GRPC_RESPONSE:
        self.queue.put(request)
        return continuation(call_details, request)


@contextmanager
def grpc_test_helper() -> Generator[None, None, None]:
    grpc_server: grpc.Server = create_app()
    try:
        grpc_server.start()
        yield None
    finally:
        grpc_server.stop(None)


@contextmanager
def fixture_loop(mock_close_loop: bool = False) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def _mock(_loop: asyncio.AbstractEventLoop = None) -> asyncio.AbstractEventLoop:
        return loop

    if mock_close_loop:
        close_loop = loop.close
    set_event_loop = asyncio.set_event_loop
    new_event_loop = asyncio.new_event_loop
    try:
        asyncio.set_event_loop = _mock  # type: ignore
        asyncio.new_event_loop = _mock
        if mock_close_loop:
            loop.close = lambda: None  # type: ignore
        yield loop
    finally:
        asyncio.set_event_loop = set_event_loop
        asyncio.new_event_loop = new_event_loop
        if mock_close_loop:
            loop.close = close_loop  # type: ignore


@contextmanager
def grpc_test_create_user_request(app: Any) -> Generator[Queue, None, None]:
    from pait.app import get_app_attribute
    from pait.app.base.grpc_route import AsyncGrpcGatewayRoute, BaseGrpcGatewayRoute

    def reinit_channel(grpc_gateway_route: BaseGrpcGatewayRoute, queue: Queue) -> None:
        if isinstance(grpc_gateway_route, AsyncGrpcGatewayRoute):
            grpc_gateway_route.reinit_channel(
                grpc.aio.insecure_channel("0.0.0.0:9000", interceptors=[AioGrpcClientInterceptor(queue)])
            )
        else:
            grpc_gateway_route.reinit_channel(
                grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000"), GrpcClientInterceptor(queue)),
            )

    with grpc_test_helper():
        queue: Queue = Queue()
        grpc_gateway_route: BaseGrpcGatewayRoute = get_app_attribute(app, "grpc_gateway_route")
        if sniffing(app) == "sanic":

            def _before_server_start(*_: Any) -> None:
                reinit_channel(grpc_gateway_route, queue)

            async def _after_server_stop(*_: Any) -> None:
                await grpc_gateway_route.channel.close()

            app.before_server_start(_before_server_start)
            app.after_server_stop(_after_server_stop)
        else:
            reinit_channel(grpc_gateway_route, queue)

        try:
            yield queue

        finally:
            if not isinstance(grpc_gateway_route, AsyncGrpcGatewayRoute):
                grpc_gateway_route.channel.close()
                # For tornado, the channel cannot be reclaimed


def grpc_test_openapi(pait_dict: dict, url_prefix: str = "/api") -> None:
    from pait.api_doc.open_api import PaitOpenAPI

    url_list: List[str] = [
        f"{url_prefix}/user/create",
        f"{url_prefix}/user/delete",
        f"{url_prefix}/user/login",
        f"{url_prefix}/user/logout",
        f"{url_prefix}/book_manager-BookManager/get_book_list",
        f"{url_prefix}/book_manager-BookManager/create_book",
        f"{url_prefix}/book_manager-BookManager/delete_book",
        f"{url_prefix}/book_manager-BookManager/get_book",
        f"{url_prefix}/book_social-BookSocial/get_book_comment",
        f"{url_prefix}/book_social-BookSocial/like_multi_book",
        f"{url_prefix}/book_social-BookSocial/get_book_like",
        f"{url_prefix}/book_social-BookSocial/comment_book",
        f"{url_prefix}/book_social-BookSocial/like_book",
    ]
    pait_openapi: PaitOpenAPI = PaitOpenAPI(pait_dict, title="test")

    # test not enable grpc method
    for url in pait_openapi.open_api_dict["paths"]:
        assert "get_uid_by_token" not in url

    for url in url_list:
        is_grpc_route: bool = url in pait_openapi.open_api_dict["paths"]
        # test url
        assert is_grpc_route

        if not is_grpc_route:
            continue
        path_dict: dict = pait_openapi.open_api_dict["paths"][url]

        # test method
        if url == f"{url_prefix}/book_social-BookSocial/get_book_like":
            method: str = "get"
        else:
            method = "post"
        assert method in path_dict
        # test tags
        assert "grpc" in path_dict[method]["tags"]
        if url.startswith(f"{url_prefix}/user"):
            assert "grpc-user" in path_dict[method]["tags"]
            if url.endswith("/create") or url.endswith("/delete"):
                assert "grpc-user-system" in path_dict[method]["tags"]
        elif url.startswith(f"{url_prefix}/book_manager"):
            assert "grpc-book_manager" in path_dict[method]["tags"]
        elif url.startswith(f"{url_prefix}/book_social"):
            assert "grpc-book_social" in path_dict[method]["tags"]

        # test summary
        if url == f"{url_prefix}/user/create":
            assert path_dict[method]["summary"] == "Create users through the system"
        elif url == f"{url_prefix}/user/login":
            assert path_dict[method]["summary"] == "User login to system"
            response_schema_key: str = path_dict["post"]["responses"][200]["content"]["application/json"]["schema"][
                "$ref"
            ]
            response_schema: dict = pait_openapi.open_api_dict["components"]["schemas"][
                response_schema_key.split("/")[-1]
            ]
            assert response_schema["title"] == "CustomerJsonResponseRespModel"
            for column in ["code", "msg", "data"]:
                assert column in response_schema["properties"]
        elif url == f"{url_prefix}/user/logout":
            assert path_dict[method]["summary"] == "User exit from the system"
        else:
            assert path_dict[method]["summary"] == ""

        # test description
        if url == f"{url_prefix}/user/delete":
            assert path_dict[method]["description"] == "This interface performs a logical delete, not a physical delete"
        else:
            assert path_dict[method]["description"] == ""

        # test parse protobuf desc to request pydantic.BaseModel
        if url == f"{url_prefix}/user/create":
            schema: dict = path_dict[method]["requestBody"]["content"]["application/json"]["schema"]
            # test miss default
            assert schema["required"] == ["uid"]

            # test field
            assert schema["properties"]["uid"]["title"] == "UID"
            assert schema["properties"]["uid"]["type"] == "string"
            assert schema["properties"]["uid"]["description"] == "user union id"
            assert schema["properties"]["uid"]["example"] == "10086"

            assert schema["properties"]["user_name"]["maxLength"] == 10
            assert schema["properties"]["user_name"]["minLength"] == 1

            assert "password" not in schema["properties"]  # test alias
            assert schema["properties"]["sex"]["default"] == 0  # test enum default
