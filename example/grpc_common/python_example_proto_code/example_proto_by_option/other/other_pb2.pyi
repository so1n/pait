"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class DemoMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    A_FIELD_NUMBER: builtins.int
    B_FIELD_NUMBER: builtins.int
    a: builtins.int
    b: typing.Text
    def __init__(self,
        *,
        a: builtins.int = ...,
        b: typing.Text = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["a",b"a","b",b"b"]) -> None: ...
global___DemoMessage = DemoMessage

class SubSubSubNestedMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPEATED_DEMO_FIELD_NUMBER: builtins.int
    @property
    def repeated_demo(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___DemoMessage]: ...
    def __init__(self,
        *,
        repeated_demo: typing.Optional[typing.Iterable[global___DemoMessage]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["repeated_demo",b"repeated_demo"]) -> None: ...
global___SubSubSubNestedMessage = SubSubSubNestedMessage

class SubSubNestedMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class MapDemoEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text
        @property
        def value(self) -> global___SubSubSubNestedMessage: ...
        def __init__(self,
            *,
            key: typing.Text = ...,
            value: typing.Optional[global___SubSubSubNestedMessage] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    MAP_DEMO_FIELD_NUMBER: builtins.int
    @property
    def map_demo(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___SubSubSubNestedMessage]: ...
    def __init__(self,
        *,
        map_demo: typing.Optional[typing.Mapping[typing.Text, global___SubSubSubNestedMessage]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["map_demo",b"map_demo"]) -> None: ...
global___SubSubNestedMessage = SubSubNestedMessage

class SubNestedMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPEATED_DEMO_FIELD_NUMBER: builtins.int
    @property
    def repeated_demo(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___SubSubNestedMessage]: ...
    def __init__(self,
        *,
        repeated_demo: typing.Optional[typing.Iterable[global___SubSubNestedMessage]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["repeated_demo",b"repeated_demo"]) -> None: ...
global___SubNestedMessage = SubNestedMessage

class NestedMessage(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    class MapDemoEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor
        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: typing.Text
        @property
        def value(self) -> global___SubNestedMessage: ...
        def __init__(self,
            *,
            key: typing.Text = ...,
            value: typing.Optional[global___SubNestedMessage] = ...,
            ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["value",b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["key",b"key","value",b"value"]) -> None: ...

    MAP_DEMO_FIELD_NUMBER: builtins.int
    @property
    def map_demo(self) -> google.protobuf.internal.containers.MessageMap[typing.Text, global___SubNestedMessage]: ...
    def __init__(self,
        *,
        map_demo: typing.Optional[typing.Mapping[typing.Text, global___SubNestedMessage]] = ...,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["map_demo",b"map_demo"]) -> None: ...
global___NestedMessage = NestedMessage
