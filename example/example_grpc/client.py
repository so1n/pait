import grpc

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc

channel: grpc.Channel = grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000"))
user_stub: user_pb2_grpc.UserStub = user_pb2_grpc.UserStub(channel)
manager_stub: manager_pb2_grpc.BookManagerStub = manager_pb2_grpc.BookManagerStub(channel)
social_stub: social_pb2_grpc.BookSocialStub = social_pb2_grpc.BookSocialStub(channel)


def get_use_aio_channel_stub_list(init_new_event_loop: bool = True) -> tuple:
    if init_new_event_loop:
        import asyncio

        asyncio.set_event_loop(asyncio.new_event_loop())

    _aio_channel: grpc.Channel = grpc.aio.insecure_channel("0.0.0.0:9000")
    _aio_user_stub: user_pb2_grpc.UserStub = user_pb2_grpc.UserStub(_aio_channel)
    _aio_manager_stub: manager_pb2_grpc.BookManagerStub = manager_pb2_grpc.BookManagerStub(_aio_channel)
    _aio_social_stub: social_pb2_grpc.BookSocialStub = social_pb2_grpc.BookSocialStub(_aio_channel)
    return _aio_user_stub, _aio_manager_stub, _aio_social_stub


if __name__ == "__main__":
    grpc.channel_ready_future(channel).result(timeout=3)
