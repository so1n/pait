import datetime
from decimal import Decimal

from google.protobuf import descriptor, json_format
from google.protobuf.timestamp_pb2 import Timestamp

# Get the original usage
_ConvertScalarFieldValue = json_format._ConvertScalarFieldValue  # type: ignore[attr-defined]


def ConvertScalarFieldValue(value, field, path, require_str=False):  # type: ignore[no-untyped-def]
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_STRING:
        if isinstance(value, (int, float)):
            # If a string type is defined, precast it
            value = str(value)
    if isinstance(value, Decimal):
        value = str(value)
    # Finally, it will be handed over to the original method to deal with it
    return _ConvertScalarFieldValue(value, field, path, require_str)


setattr(json_format, "_ConvertScalarFieldValue", ConvertScalarFieldValue)


class Parser(json_format._Parser):  # type: ignore[name-defined]
    def _ConvertGenericMessage(self, value, message, path):  # type: ignore[no-untyped-def]
        # Special handling of the datetime parameter
        if isinstance(message, Timestamp) and isinstance(value, int):
            message.FromDatetime(datetime.datetime.fromtimestamp(value))
            return
        elif isinstance(value, datetime.datetime):
            message.FromDatetime(value)
            return
        elif isinstance(value, datetime.date):
            message.FromDatetime(datetime.datetime.combine(value, datetime.datetime.min.time()))
            return
        # Call the original method
        super()._ConvertGenericMessage(value, message, path)


def parse_dict(js_dict, message, ignore_unknown_fields=False, descriptor_pool=None, max_recursion_depth=100):  # type: ignore[no-untyped-def]  # noqa
    parser = Parser(ignore_unknown_fields, descriptor_pool, max_recursion_depth)
    parser.ConvertMessage(js_dict, message, "")
    return message
