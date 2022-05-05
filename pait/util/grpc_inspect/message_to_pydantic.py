import datetime
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from google.protobuf.descriptor import Descriptor, FieldDescriptor  # type: ignore
from google.protobuf.message import Message  # type: ignore
from google.protobuf.timestamp_pb2 import Timestamp  # type: ignore
from pydantic import BaseModel, validator
from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import NoArgAnyCallable

from pait.field import Depends
from pait.util import create_pydantic_model

type_dict: Dict[str, Type] = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT64: int,
    FieldDescriptor.TYPE_UINT64: int,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_FIXED64: float,
    FieldDescriptor.TYPE_FIXED32: float,
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: str,
    FieldDescriptor.TYPE_BYTES: str,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_SFIXED32: float,
    FieldDescriptor.TYPE_SFIXED64: float,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: int,
}

GRPC_TIMESTAMP_HANDLER_TUPLE_T = Tuple[Any, Optional[Callable[[Any, Any], Timestamp]]]


def grpc_timestamp_int_handler(cls: Any, v: int) -> Timestamp:
    t: Timestamp = Timestamp()

    if v:
        t.FromDatetime(datetime.datetime.fromtimestamp(v))
    return t


def _parse_msg_to_pydantic_model(
    descriptor: Descriptor,
    grpc_timestamp_handler_tuple: GRPC_TIMESTAMP_HANDLER_TUPLE_T,
    default_field: Type[FieldInfo] = FieldInfo,
    request_param_field_dict: Optional[Dict[str, Union[Type[FieldInfo], Depends]]] = None,
) -> Type[BaseModel]:
    request_param_field_dict = request_param_field_dict or {}
    annotation_dict: Dict[str, Tuple[Type, Any]] = {}
    validators: Dict[str, classmethod] = {}
    timestamp_handler_field_silt: List[str] = []
    timestamp_type, _grpc_timestamp_handler = grpc_timestamp_handler_tuple

    for column in descriptor.fields:
        field: Union[Type[FieldInfo], Depends] = request_param_field_dict.get(column.name, default_field)

        type_: Any = type_dict.get(column.type, None)
        name: str = column.name
        default: Any = Undefined
        default_factory: Optional[NoArgAnyCallable] = None

        if column.type == FieldDescriptor.TYPE_MESSAGE:
            if column.message_type.name == "Timestamp":
                # support google.protobuf.Timestamp
                type_ = timestamp_type
                timestamp_handler_field_silt.append(column.name)
            elif column.message_type.name.endswith("Entry"):
                # support google.protobuf.MapEntry
                key, value = column.message_type.fields
                key_type: Any = (
                    type_dict[key.type]
                    if not key.message_type
                    else _parse_msg_to_pydantic_model(key.message_type, grpc_timestamp_handler_tuple)
                )
                value_type: Any = (
                    type_dict[value.type]
                    if not value.message_type
                    else _parse_msg_to_pydantic_model(value.message_type, grpc_timestamp_handler_tuple)
                )
                type_ = Dict[key_type, value_type]
            elif column.message_type.name == "Struct":
                # support google.protobuf.Struct
                type_ = Dict[str, Any]
            else:
                # support google.protobuf.Message
                type_ = _parse_msg_to_pydantic_model(column.message_type, grpc_timestamp_handler_tuple)
        elif column.type == FieldDescriptor.TYPE_ENUM:
            # support google.protobuf.Enum
            type_ = IntEnum(column.enum_type.name, {v.name: v.number for v in column.enum_type.values})  # type: ignore
            default = 0
        else:
            if column.label == FieldDescriptor.LABEL_REQUIRED:
                default = ...
            elif column.label == FieldDescriptor.LABEL_REPEATED:
                type_ = List[type_]  # type: ignore
                default_factory = list
            else:
                default = column.default_value

        if isinstance(field, Depends):
            use_field: Any = field
        else:
            use_field = field(default=default, default_factory=default_factory)
        annotation_dict[name] = (type_, use_field)

    if timestamp_handler_field_silt and _grpc_timestamp_handler:
        validators["timestamp_validator"] = validator(
            *timestamp_handler_field_silt,
            allow_reuse=True,
            check_fields=True,
            always=True,
        )(_grpc_timestamp_handler)
    return create_pydantic_model(annotation_dict, class_name=descriptor.name, pydantic_validators=validators or None)


def parse_msg_to_pydantic_model(
    msg: Union[Type[Message], Descriptor],
    default_field: Type[FieldInfo] = FieldInfo,
    request_param_field_dict: Optional[Dict[str, Union[Type[FieldInfo], Depends]]] = None,
    grpc_timestamp_handler_tuple: Optional[GRPC_TIMESTAMP_HANDLER_TUPLE_T] = None,
) -> Type[BaseModel]:
    """
    Parse a message to a pydantic model
    :param msg: grpc Message or descriptor
    :param default_field: gen pydantic_model default Field,
        apply only to the outermost pydantic model
    :param request_param_field_dict: The generated pydantic model corresponds to the field of the attribute,
        apply only to the outermost pydantic model
    :param grpc_timestamp_handler_tuple:
    """
    return _parse_msg_to_pydantic_model(
        msg if isinstance(msg, Descriptor) else msg.DESCRIPTOR,
        grpc_timestamp_handler_tuple or (str, None),
        default_field=default_field,
        request_param_field_dict=request_param_field_dict,
    )
