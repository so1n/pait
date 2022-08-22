# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: example_proto_by_option/user/user.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from example.example_grpc.python_example_proto_code.example_proto_by_option.common import p2p_validate_pb2 as example__proto__by__option_dot_common_dot_p2p__validate__pb2
from pait import api_pb2 as pait_dot_api__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'example_proto_by_option/user/user.proto\x12\x04user\x1a\x1bgoogle/protobuf/empty.proto\x1a\x31\x65xample_proto_by_option/common/p2p_validate.proto\x1a\x0epait/api.proto\"\x82\x02\n\x11\x43reateUserRequest\x12\x42\n\x03uid\x18\x01 \x01(\tB5\x8a\x43\x05r\x03\xd0\x01\x01\x8a\x43\nr\x08\xf2\x01\x05\x31\x30\x30\x38\x36\x8a\x43\x08r\x06\x92\x02\x03UID\x8a\x43\x12r\x10\xe2\x01\ruser union id\x12>\n\tuser_name\x18\x02 \x01(\tB+\x8a\x43\x0er\x0c\xe2\x01\tuser name\x8a\x43\x04r\x02\x18\x01\x8a\x43\x04r\x02 \n\x8a\x43\tr\x07\xf2\x01\x04so1n\x12M\n\x08password\x18\x03 \x01(\tB;\x8a\x43\x12r\x10\xe2\x01\ruser password\x8a\x43\x07r\x05\xda\x01\x02pw\x8a\x43\x04r\x02\x18\x06\x8a\x43\x04r\x02 \x12\x8a\x43\x0br\t\xf2\x01\x06\x31\x32\x33\x34\x35\x36\x12\x1a\n\x03sex\x18\x04 \x01(\x0e\x32\r.user.SexType\" \n\x11\x44\x65leteUserRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\"1\n\x10LoginUserRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\xb0\x01\n\x0fLoginUserResult\x12:\n\x03uid\x18\x01 \x01(\tB-\x8a\x43\nr\x08\xf2\x01\x05\x31\x30\x30\x38\x36\x8a\x43\x08r\x06\x92\x02\x03UID\x8a\x43\x12r\x10\xe2\x01\ruser union id\x12>\n\tuser_name\x18\x02 \x01(\tB+\x8a\x43\x0er\x0c\xe2\x01\tuser name\x8a\x43\x04r\x02\x18\x01\x8a\x43\x04r\x02 \n\x8a\x43\tr\x07\xf2\x01\x04so1n\x12!\n\x05token\x18\x03 \x01(\tB\x12\x8a\x43\x0fr\r\xe2\x01\nuser token\"9\n\x11LogoutUserRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x17\n\x05token\x18\x02 \x01(\tB\x08\x8a\x43\x05r\x03\xb8\x01\x00\"%\n\x14GetUidByTokenRequest\x12\r\n\x05token\x18\x01 \x01(\t\"\"\n\x13GetUidByTokenResult\x12\x0b\n\x03uid\x18\x01 \x01(\t*\x1d\n\x07SexType\x12\x07\n\x03man\x10\x00\x12\t\n\x05women\x10\x01\x32\xcf\x06\n\x04User\x12y\n\x10get_uid_by_token\x12\x1a.user.GetUidByTokenRequest\x1a\x19.user.GetUidByTokenResult\".\x8a\xd3\xe4\x93\x02(\xaa\x01\x04user\xb2\x01\x1e\n\tgrpc-user\x12\x11grpc_user_service\x12\x93\x01\n\x0blogout_user\x12\x17.user.LogoutUserRequest\x1a\x16.google.protobuf.Empty\"S\x8a\xd3\xe4\x93\x02MJ\x0e\n\x0c/user/logout\xb2\x01\x1e\n\tgrpc-user\x12\x11grpc_user_service\xba\x01\x19User exit from the system\x12\x8a\x01\n\nlogin_user\x12\x16.user.LoginUserRequest\x1a\x15.user.LoginUserResult\"M\x8a\xd3\xe4\x93\x02GJ\r\n\x0b/user/login\xb2\x01\x1e\n\tgrpc-user\x12\x11grpc_user_service\xba\x01\x14User login to system\x12\xc2\x01\n\x0b\x63reate_user\x12\x17.user.CreateUserRequest\x1a\x16.google.protobuf.Empty\"\x81\x01\x8a\xd3\xe4\x93\x02{J\x0e\n\x0c/user/create\xb2\x01\x1e\n\tgrpc-user\x12\x11grpc_user_service\xb2\x01%\n\x10grpc-user-system\x12\x11grpc_user_service\xba\x01\x1f\x43reate users through the system\x12\xe3\x01\n\x0b\x64\x65lete_user\x12\x17.user.DeleteUserRequest\x1a\x16.google.protobuf.Empty\"\xa2\x01\x8a\xd3\xe4\x93\x02\x9b\x01J\x0e\n\x0c/user/delete\xb2\x01\x1e\n\tgrpc-user\x12\x11grpc_user_service\xb2\x01%\n\x10grpc-user-system\x12\x11grpc_user_service\xc2\x01?This interface performs a logical delete, not a physical deleteb\x06proto3')

_SEXTYPE = DESCRIPTOR.enum_types_by_name['SexType']
SexType = enum_type_wrapper.EnumTypeWrapper(_SEXTYPE)
man = 0
women = 1


_CREATEUSERREQUEST = DESCRIPTOR.message_types_by_name['CreateUserRequest']
_DELETEUSERREQUEST = DESCRIPTOR.message_types_by_name['DeleteUserRequest']
_LOGINUSERREQUEST = DESCRIPTOR.message_types_by_name['LoginUserRequest']
_LOGINUSERRESULT = DESCRIPTOR.message_types_by_name['LoginUserResult']
_LOGOUTUSERREQUEST = DESCRIPTOR.message_types_by_name['LogoutUserRequest']
_GETUIDBYTOKENREQUEST = DESCRIPTOR.message_types_by_name['GetUidByTokenRequest']
_GETUIDBYTOKENRESULT = DESCRIPTOR.message_types_by_name['GetUidByTokenResult']
CreateUserRequest = _reflection.GeneratedProtocolMessageType('CreateUserRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEUSERREQUEST,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.CreateUserRequest)
  })
_sym_db.RegisterMessage(CreateUserRequest)

DeleteUserRequest = _reflection.GeneratedProtocolMessageType('DeleteUserRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELETEUSERREQUEST,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.DeleteUserRequest)
  })
_sym_db.RegisterMessage(DeleteUserRequest)

LoginUserRequest = _reflection.GeneratedProtocolMessageType('LoginUserRequest', (_message.Message,), {
  'DESCRIPTOR' : _LOGINUSERREQUEST,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.LoginUserRequest)
  })
_sym_db.RegisterMessage(LoginUserRequest)

LoginUserResult = _reflection.GeneratedProtocolMessageType('LoginUserResult', (_message.Message,), {
  'DESCRIPTOR' : _LOGINUSERRESULT,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.LoginUserResult)
  })
_sym_db.RegisterMessage(LoginUserResult)

LogoutUserRequest = _reflection.GeneratedProtocolMessageType('LogoutUserRequest', (_message.Message,), {
  'DESCRIPTOR' : _LOGOUTUSERREQUEST,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.LogoutUserRequest)
  })
_sym_db.RegisterMessage(LogoutUserRequest)

GetUidByTokenRequest = _reflection.GeneratedProtocolMessageType('GetUidByTokenRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETUIDBYTOKENREQUEST,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.GetUidByTokenRequest)
  })
_sym_db.RegisterMessage(GetUidByTokenRequest)

GetUidByTokenResult = _reflection.GeneratedProtocolMessageType('GetUidByTokenResult', (_message.Message,), {
  'DESCRIPTOR' : _GETUIDBYTOKENRESULT,
  '__module__' : 'example_proto_by_option.user.user_pb2'
  # @@protoc_insertion_point(class_scope:user.GetUidByTokenResult)
  })
_sym_db.RegisterMessage(GetUidByTokenResult)

_USER = DESCRIPTOR.services_by_name['User']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CREATEUSERREQUEST.fields_by_name['uid']._options = None
  _CREATEUSERREQUEST.fields_by_name['uid']._serialized_options = b'\212C\005r\003\320\001\001\212C\nr\010\362\001\00510086\212C\010r\006\222\002\003UID\212C\022r\020\342\001\ruser union id'
  _CREATEUSERREQUEST.fields_by_name['user_name']._options = None
  _CREATEUSERREQUEST.fields_by_name['user_name']._serialized_options = b'\212C\016r\014\342\001\tuser name\212C\004r\002\030\001\212C\004r\002 \n\212C\tr\007\362\001\004so1n'
  _CREATEUSERREQUEST.fields_by_name['password']._options = None
  _CREATEUSERREQUEST.fields_by_name['password']._serialized_options = b'\212C\022r\020\342\001\ruser password\212C\007r\005\332\001\002pw\212C\004r\002\030\006\212C\004r\002 \022\212C\013r\t\362\001\006123456'
  _LOGINUSERRESULT.fields_by_name['uid']._options = None
  _LOGINUSERRESULT.fields_by_name['uid']._serialized_options = b'\212C\nr\010\362\001\00510086\212C\010r\006\222\002\003UID\212C\022r\020\342\001\ruser union id'
  _LOGINUSERRESULT.fields_by_name['user_name']._options = None
  _LOGINUSERRESULT.fields_by_name['user_name']._serialized_options = b'\212C\016r\014\342\001\tuser name\212C\004r\002\030\001\212C\004r\002 \n\212C\tr\007\362\001\004so1n'
  _LOGINUSERRESULT.fields_by_name['token']._options = None
  _LOGINUSERRESULT.fields_by_name['token']._serialized_options = b'\212C\017r\r\342\001\nuser token'
  _LOGOUTUSERREQUEST.fields_by_name['token']._options = None
  _LOGOUTUSERREQUEST.fields_by_name['token']._serialized_options = b'\212C\005r\003\270\001\000'
  _USER.methods_by_name['get_uid_by_token']._options = None
  _USER.methods_by_name['get_uid_by_token']._serialized_options = b'\212\323\344\223\002(\252\001\004user\262\001\036\n\tgrpc-user\022\021grpc_user_service'
  _USER.methods_by_name['logout_user']._options = None
  _USER.methods_by_name['logout_user']._serialized_options = b'\212\323\344\223\002MJ\016\n\014/user/logout\262\001\036\n\tgrpc-user\022\021grpc_user_service\272\001\031User exit from the system'
  _USER.methods_by_name['login_user']._options = None
  _USER.methods_by_name['login_user']._serialized_options = b'\212\323\344\223\002GJ\r\n\013/user/login\262\001\036\n\tgrpc-user\022\021grpc_user_service\272\001\024User login to system'
  _USER.methods_by_name['create_user']._options = None
  _USER.methods_by_name['create_user']._serialized_options = b'\212\323\344\223\002{J\016\n\014/user/create\262\001\036\n\tgrpc-user\022\021grpc_user_service\262\001%\n\020grpc-user-system\022\021grpc_user_service\272\001\037Create users through the system'
  _USER.methods_by_name['delete_user']._options = None
  _USER.methods_by_name['delete_user']._serialized_options = b'\212\323\344\223\002\233\001J\016\n\014/user/delete\262\001\036\n\tgrpc-user\022\021grpc_user_service\262\001%\n\020grpc-user-system\022\021grpc_user_service\302\001?This interface performs a logical delete, not a physical delete'
  _SEXTYPE._serialized_start=804
  _SEXTYPE._serialized_end=833
  _CREATEUSERREQUEST._serialized_start=146
  _CREATEUSERREQUEST._serialized_end=404
  _DELETEUSERREQUEST._serialized_start=406
  _DELETEUSERREQUEST._serialized_end=438
  _LOGINUSERREQUEST._serialized_start=440
  _LOGINUSERREQUEST._serialized_end=489
  _LOGINUSERRESULT._serialized_start=492
  _LOGINUSERRESULT._serialized_end=668
  _LOGOUTUSERREQUEST._serialized_start=670
  _LOGOUTUSERREQUEST._serialized_end=727
  _GETUIDBYTOKENREQUEST._serialized_start=729
  _GETUIDBYTOKENREQUEST._serialized_end=766
  _GETUIDBYTOKENRESULT._serialized_start=768
  _GETUIDBYTOKENRESULT._serialized_end=802
  _USER._serialized_start=836
  _USER._serialized_end=1683
# @@protoc_insertion_point(module_scope)
