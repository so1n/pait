from typing import Any, Dict, List, Optional, Tuple, Type, Union

from google.protobuf.descriptor import Descriptor, FieldDescriptor  # type: ignore
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic.fields import FieldInfo

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


def parse_msg_to_pydantic_model(
    msg: Union[Type[Message], Descriptor],
    default_field: Type[FieldInfo] = FieldInfo,
    request_param_field_dict: Optional[Dict[str, Union[Type[FieldInfo], Depends]]] = None,
) -> Type[BaseModel]:
    """
    Parse a message to a pydantic model
    :param msg: grpc Message or descriptor
    :param default_field: gen pydantic_model default Field,
        apply only to the outermost pydantic model
    :param request_param_field_dict: The generated pydantic model corresponds to the field of the attribute,
        apply only to the outermost pydantic model
    """
    request_param_field_dict = request_param_field_dict or {}

    annotation_dict: Dict[str, Tuple[Type, Any]] = {}

    if isinstance(msg, Descriptor):
        descriptor: Descriptor = msg
    else:
        descriptor = msg.DESCRIPTOR

    for column in descriptor.fields:
        field: Union[Type[FieldInfo], Depends] = request_param_field_dict.get(column.name, default_field)

        if column.type == FieldDescriptor.TYPE_MESSAGE:
            annotation_dict[column.name] = (parse_msg_to_pydantic_model(column.message_type), field)
        elif isinstance(field, Depends):
            annotation_dict[column.name] = (type_dict[column.type], field)
        else:
            name: str = column.name
            type_ = type_dict[column.type]

            if column.label == FieldDescriptor.LABEL_REQUIRED:
                annotation_dict[name] = (type_, ...)
            elif column.label == FieldDescriptor.LABEL_REPEATED:
                type_ = List[type_]  # type: ignore
                annotation_dict[name] = (type_, field(default_factory=lambda: column.default_value))
            else:
                annotation_dict[name] = (type_, field(default=column.default_value))
    return create_pydantic_model(annotation_dict, class_name=descriptor.name)
