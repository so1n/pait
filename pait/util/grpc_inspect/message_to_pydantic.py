from typing import Any, Dict, Tuple, Type

from google.protobuf.descriptor import FieldDescriptor  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from pait.util import create_pydantic_model

type_dict: Dict[str, type] = {
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


def parse_msg_to_pydantic_model(msg: Type[Message], field: Type[FieldInfo] = FieldInfo) -> Type[BaseModel]:

    annotation_dict: Dict[str, Tuple[Type, Any]] = {}
    for column in msg.DESCRIPTOR.fields:
        annotation_dict[column.name] = (type_dict[column.type], field(default=column.default_value))
    return create_pydantic_model(annotation_dict, class_name=msg.DESCRIPTOR.name)
