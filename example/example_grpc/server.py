import logging
from concurrent import futures
from typing import Any, List, Optional

import grpc

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc as manager_service
from example.example_grpc.python_example_proto_code.example_proto.book import social_pb2_grpc as social_service
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc as user_service
from pait.util.grpc_inspect.stub import ParseStub

logger: logging.Logger = logging.getLogger()


class UserService(user_service.UserServicer):
    pass


class ManagerService(manager_service.BookManagerServicer):
    pass


class SocialService(social_service.BookSocialServicer):
    pass


helper_channel: grpc.Channel = grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000"))


def auto_gen_service_method(stub: Any, service: Any) -> None:
    """auto return response"""
    parser: ParseStub = ParseStub(stub)
    for method, grpc_model in parser.method_dict.items():
        method_name: str = method.split("/")[-1]

        def _func(self: Any, request: Any, context: Any) -> Any:
            logger.info(f"{self.__class__.__name__} receive request:{request}")
            return grpc_model.response()

        setattr(service, method_name, _func)


auto_gen_service_method(user_service.UserStub(helper_channel), UserService)
auto_gen_service_method(manager_service.BookManagerStub(helper_channel), ManagerService)
auto_gen_service_method(social_service.BookSocialStub(helper_channel), SocialService)


def create_app(
    host_post: str = "0.0.0.0:9000", max_workers: int = 10, interceptor_list: Optional[List] = None
) -> grpc.Server:
    server: grpc.Server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        interceptors=interceptor_list,
    )
    manager_service.add_BookManagerServicer_to_server(ManagerService(), server)
    user_service.add_UserServicer_to_server(UserService(), server)
    social_service.add_BookSocialServicer_to_server(SocialService(), server)
    server.add_insecure_port(host_post)
    return server


def main() -> None:
    host_post: str = "0.0.0.0:9000"
    server: grpc.Server = create_app(host_post=host_post)
    server.start()
    try:
        for generic_handler in server._state.generic_handlers:  # type: ignore
            logger.info(
                f"add service name:{generic_handler.service_name()} cnt:{len(generic_handler._method_handlers)}"
            )
        logger.info(f"server run in {host_post}")
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s %(levelname)s] %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.DEBUG
    )
    main()
