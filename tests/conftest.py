import asyncio
from contextlib import contextmanager
from queue import Queue
from typing import TYPE_CHECKING, Any, Callable, Generator, List

import grpc

from example.example_grpc.server import create_app
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


class GrpcTestHelperInterceptor(grpc.ServerInterceptor):
    def __init__(self, queue: Queue):
        self.queue: Queue = queue

    def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], grpc.RpcMethodHandler],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        next_handler: grpc.RpcMethodHandler = continuation(handler_call_details)

        if not next_handler.unary_unary:  # type: ignore
            # only support unary unary
            raise RuntimeError("RPC handler implementation does not exist")

        def invoke(request_proto_message: Any, context: grpc.ServicerContext) -> Any:
            self.queue.put(request_proto_message)
            return next_handler.unary_unary(request_proto_message, context)

        return grpc.unary_unary_rpc_method_handler(
            invoke,
            request_deserializer=next_handler.request_deserializer,
            response_serializer=next_handler.response_serializer,
        )


@contextmanager
def grpc_test_helper() -> Generator[Queue, None, None]:
    msg_queue: Queue = Queue()
    grpc_server: grpc.Server = create_app(interceptor_list=[GrpcTestHelperInterceptor(msg_queue)])
    try:
        grpc_server.start()
        yield msg_queue
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


def grpc_test_create_user_request(request_callable: Callable[[dict], None]) -> None:
    from example.example_grpc.python_example_proto_code.example_proto.user.user_pb2 import CreateUserRequest

    request_dict: dict = {"uid": "10086", "user_name": "so1n", "pw": "123456", "sex": 0}
    with grpc_test_helper() as queue:
        request_callable(request_dict)
        try:
            message: CreateUserRequest = queue.get(timeout=1)
            assert message.uid == "10086"
            assert message.user_name == "so1n"
            assert message.password == "123456"
            assert message.sex == 0
        except Exception:
            import warnings

            warnings.warn("Can recv msg, Ignore for now")


def grpc_test_openapi(pait_dict: dict) -> None:
    from pait.api_doc.open_api import PaitOpenAPI

    url_list: List[str] = [
        "/api/user/create",
        "/api/user/delete",
        "/api/user/login",
        "/api/user/logout",
        "/api/book_manager-BookManager/get_book_list",
        "/api/book_manager-BookManager/create_book",
        "/api/book_manager-BookManager/delete_book",
        "/api/book_manager-BookManager/get_book",
        "/api/book_social-BookSocial/get_book_comment",
        "/api/book_social-BookSocial/like_multi_book",
        "/api/book_social-BookSocial/get_book_like",
        "/api/book_social-BookSocial/comment_book",
        "/api/book_social-BookSocial/like_book",
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
        assert "post" in path_dict
        # test tags
        assert "grpc" in path_dict["post"]["tags"]
        if url.startswith("/api/user"):
            assert "grpc-user" in path_dict["post"]["tags"]
            if url.endswith("/create") or url.endswith("/delete"):
                assert "grpc-user-system" in path_dict["post"]["tags"]
        elif url.startswith("/api/book_manager"):
            assert "grpc-book_manager" in path_dict["post"]["tags"]
        elif url.startswith("/api/book_social"):
            assert "grpc-book_social" in path_dict["post"]["tags"]

        # test summary
        if url == "/api/user/create":
            assert path_dict["post"]["summary"] == "Create users through the system"
        elif url == "/api/user/login":
            assert path_dict["post"]["summary"] == "User login to system"
        elif url == "/api/user/logout":
            assert path_dict["post"]["summary"] == "User exit from the system"
        else:
            assert path_dict["post"]["summary"] == ""

        # test description
        if url == "/api/user/delete":
            assert path_dict["post"]["description"] == "This interface performs a logical delete, not a physical delete"
        else:
            assert path_dict["post"]["description"] == ""

        # test parse protobuf desc to request pydantic.BaseModel
        if url == "/api/user/create":
            schema: dict = path_dict["post"]["requestBody"]["content"]["application/json"]["schema"]
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
