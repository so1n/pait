# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from example.grpc_common.python_example_proto_code.example_proto.user import user_pb2 as example__proto_dot_user_dot_user__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class UserStub(object):
    """pait: {"group": "user", "tag": [["grpc-user", "grpc_user_service"]]}
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.get_uid_by_token = channel.unary_unary(
                '/user.User/get_uid_by_token',
                request_serializer=example__proto_dot_user_dot_user__pb2.GetUidByTokenRequest.SerializeToString,
                response_deserializer=example__proto_dot_user_dot_user__pb2.GetUidByTokenResult.FromString,
                )
        self.logout_user = channel.unary_unary(
                '/user.User/logout_user',
                request_serializer=example__proto_dot_user_dot_user__pb2.LogoutUserRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.login_user = channel.unary_unary(
                '/user.User/login_user',
                request_serializer=example__proto_dot_user_dot_user__pb2.LoginUserRequest.SerializeToString,
                response_deserializer=example__proto_dot_user_dot_user__pb2.LoginUserResult.FromString,
                )
        self.create_user = channel.unary_unary(
                '/user.User/create_user',
                request_serializer=example__proto_dot_user_dot_user__pb2.CreateUserRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.delete_user = channel.unary_unary(
                '/user.User/delete_user',
                request_serializer=example__proto_dot_user_dot_user__pb2.DeleteUserRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class UserServicer(object):
    """pait: {"group": "user", "tag": [["grpc-user", "grpc_user_service"]]}
    """

    def get_uid_by_token(self, request, context):
        """The interface should not be exposed for external use
        pait: {"enable": false}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def logout_user(self, request, context):
        """pait: {"summary": "User exit from the system", "url": "/user/logout"}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def login_user(self, request, context):
        """pait: {"summary": "User login to system", "url": "/user/login"}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def create_user(self, request, context):
        """pait: {"tag": [["grpc-user", "grpc_user_service"], ["grpc-user-system", "grpc_user_service"]]}
        pait: {"summary": "Create users through the system", "url": "/user/create"}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def delete_user(self, request, context):
        """pait: {"url": "/user/delete", "tag": [["grpc-user", "grpc_user_service"], ["grpc-user-system", "grpc_user_service"]]}
        pait: {"desc": "This interface performs a logical delete, not a physical delete"}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'get_uid_by_token': grpc.unary_unary_rpc_method_handler(
                    servicer.get_uid_by_token,
                    request_deserializer=example__proto_dot_user_dot_user__pb2.GetUidByTokenRequest.FromString,
                    response_serializer=example__proto_dot_user_dot_user__pb2.GetUidByTokenResult.SerializeToString,
            ),
            'logout_user': grpc.unary_unary_rpc_method_handler(
                    servicer.logout_user,
                    request_deserializer=example__proto_dot_user_dot_user__pb2.LogoutUserRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'login_user': grpc.unary_unary_rpc_method_handler(
                    servicer.login_user,
                    request_deserializer=example__proto_dot_user_dot_user__pb2.LoginUserRequest.FromString,
                    response_serializer=example__proto_dot_user_dot_user__pb2.LoginUserResult.SerializeToString,
            ),
            'create_user': grpc.unary_unary_rpc_method_handler(
                    servicer.create_user,
                    request_deserializer=example__proto_dot_user_dot_user__pb2.CreateUserRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'delete_user': grpc.unary_unary_rpc_method_handler(
                    servicer.delete_user,
                    request_deserializer=example__proto_dot_user_dot_user__pb2.DeleteUserRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'user.User', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class User(object):
    """pait: {"group": "user", "tag": [["grpc-user", "grpc_user_service"]]}
    """

    @staticmethod
    def get_uid_by_token(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.User/get_uid_by_token',
            example__proto_dot_user_dot_user__pb2.GetUidByTokenRequest.SerializeToString,
            example__proto_dot_user_dot_user__pb2.GetUidByTokenResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def logout_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.User/logout_user',
            example__proto_dot_user_dot_user__pb2.LogoutUserRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def login_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.User/login_user',
            example__proto_dot_user_dot_user__pb2.LoginUserRequest.SerializeToString,
            example__proto_dot_user_dot_user__pb2.LoginUserResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def create_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.User/create_user',
            example__proto_dot_user_dot_user__pb2.CreateUserRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def delete_user(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/user.User/delete_user',
            example__proto_dot_user_dot_user__pb2.DeleteUserRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)