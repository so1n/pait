import logging
from concurrent import futures
from typing import Any, Callable, List, Optional

import grpc

from example.grpc_common.python_example_proto_code.example_proto.book import manager_pb2_grpc as manager_service
from example.grpc_common.python_example_proto_code.example_proto.book import social_pb2_grpc as social_service
from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2_grpc as user_service
from example.grpc_common.python_example_proto_code.example_proto_by_option.book import (
    manager_pb2_grpc as manager_by_option_service,
)
from example.grpc_common.python_example_proto_code.example_proto_by_option.book import (
    social_pb2_grpc as social_by_option_service,
)
from example.grpc_common.python_example_proto_code.example_proto_by_option.user import (
    user_pb2_grpc as user_by_option_service,
)
from pait.grpc.inspect import ParseStub

logger: logging.Logger = logging.getLogger()


class UserService(user_service.UserServicer):
    pass


class ManagerService(manager_service.BookManagerServicer):
    pass


class SocialService(social_service.BookSocialServicer):
    pass


class UserByOptionService(user_by_option_service.UserServicer):
    pass


class ManagerByOptionService(manager_by_option_service.BookManagerServicer):
    pass


class SocialByOptionService(social_by_option_service.BookSocialServicer):
    pass


def auto_gen_service_method(stub: Any, service: Any) -> None:
    """auto return response"""
    parser: ParseStub = ParseStub(stub)
    for method, grpc_model_list in parser.method_list_dict.items():
        for grpc_model in grpc_model_list:
            method_name: str = method.split("/")[-1]

            def gen_func(response: Any) -> Callable:
                if method_name == "get_uid_by_token":

                    def _func(self: Any, request: Any, context: Any) -> Any:
                        logger.info(f"{self.__class__.__name__} receive request:{request}")
                        token: str = request.token
                        if token == "fail_token":
                            # test not token
                            return response()
                        else:
                            return response(uid=request.token)

                else:

                    def _func(self: Any, request: Any, context: Any) -> Any:
                        logger.info(f"{self.__class__.__name__} receive request:{request}")
                        return response()

                return _func

            setattr(service, method_name, gen_func(grpc_model.response))


auto_gen_service_method(user_service.UserStub, UserService)
auto_gen_service_method(manager_service.BookManagerStub, ManagerService)
auto_gen_service_method(social_service.BookSocialStub, SocialService)

auto_gen_service_method(user_by_option_service.UserStub, UserByOptionService)
auto_gen_service_method(manager_by_option_service.BookManagerStub, ManagerByOptionService)
auto_gen_service_method(social_by_option_service.BookSocialStub, SocialByOptionService)


def create_app(
    host_post: str = "0.0.0.0:9000", max_workers: int = 10, interceptor_list: Optional[List] = None
) -> grpc.Server:
    server: grpc.Server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        interceptors=interceptor_list,
    )
    manager_service.add_BookManagerServicer_to_server(ManagerService(), server)  # type: ignore
    user_service.add_UserServicer_to_server(UserService(), server)  # type: ignore
    social_service.add_BookSocialServicer_to_server(SocialService(), server)  # type: ignore
    manager_by_option_service.add_BookManagerServicer_to_server(ManagerByOptionService, server)  # type: ignore
    user_by_option_service.add_UserServicer_to_server(UserByOptionService(), server)  # type: ignore
    social_by_option_service.add_BookSocialServicer_to_server(SocialByOptionService(), server)  # type: ignore
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
