import grpc

from example.example_grpc.python_example_proto_code.example_proto.book import manager_pb2_grpc, social_pb2_grpc
from example.example_grpc.python_example_proto_code.example_proto.user import user_pb2_grpc

channel: grpc.Channel = grpc.intercept_channel(grpc.insecure_channel("0.0.0.0:9000"))
aio_channel: grpc.Channel = grpc.aio.insecure_channel("0.0.0.0:9000")
user_stub: user_pb2_grpc.UserStub = user_pb2_grpc.UserStub(channel)
manager_stub: manager_pb2_grpc.BookManagerStub = manager_pb2_grpc.BookManagerStub(channel)
social_stub: social_pb2_grpc.BookSocialStub = social_pb2_grpc.BookSocialStub(channel)
aio_user_stub: user_pb2_grpc.UserStub = user_pb2_grpc.UserStub(aio_channel)
aio_manager_stub: manager_pb2_grpc.BookManagerStub = manager_pb2_grpc.BookManagerStub(aio_channel)
aio_social_stub: social_pb2_grpc.BookSocialStub = social_pb2_grpc.BookSocialStub(aio_channel)


if __name__ == "__main__":
    grpc.channel_ready_future(channel).result(timeout=3)
