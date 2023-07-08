import inspect
import typing
from typing import Any, Callable, Generator, List, Optional, Set, Type, Union, _GenericAlias  # type: ignore

import typing_extensions

from pait.exceptions import ParseTypeError

try:
    from typing import is_typeddict  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import is_typeddict

_PYTHON_ORIGIN_TYPE_SET: Set[Optional[type]] = {bool, dict, float, int, list, str, tuple, type(None), None, set}
_TYPING_NOT_PARSE_TYPE_SET: set = {
    typing.Any,
    typing.Generic,
    typing_extensions.Never,
    typing_extensions.NoReturn,
    typing_extensions.Self,
    typing_extensions.ClassVar,
    typing_extensions.Final,
}
__all__ = ["parse_typing", "is_type"]


def parse_typing(_type: Any, _is_typeddict: Optional[Callable[[type], bool]] = None) -> List[Type]:
    """Get Python Type through typing as much as possible
    >>> from typing import Dict
    >>> assert [dict] == parse_typing(dict)
    >>> assert [list] == parse_typing(List)
    >>> assert [list] == parse_typing(List[str])
    >>> assert [dict] == parse_typing(Dict)
    >>> assert [set] == parse_typing(typing.Set)
    >>> assert [dict] == parse_typing(Union[dict])
    >>> assert [dict] == parse_typing(Union[Dict])
    >>> assert [dict] == parse_typing(Union[Dict[str, Any]])
    >>> assert [dict] == parse_typing(typing.AsyncIterator[Dict])
    >>> assert [dict] == parse_typing(typing.Iterator[Dict])
    >>> assert [dict] == parse_typing(typing.Generator[Dict, None, None])
    >>> assert [dict] == parse_typing(typing.AsyncGenerator[Dict, None])
    >>> assert [tuple] == parse_typing(typing.Tuple[str, int])
    >>> assert [dict] == parse_typing(typing_extensions.TypedDict)
    >>> # multi value
    >>> assert [dict, str, int] == parse_typing(Union[Dict, str, int])
    >>> assert [dict, type(None)] == parse_typing(Optional[Dict])
    >>> assert [dict, type(None)] == parse_typing(Optional[dict])
    >>> # Relatively rarely used scenes
    >>> assert [int] == parse_typing(typing.NewType("UserId", int))
    >>> assert [int] == parse_typing(typing.Callable[[], int])
    >>> assert [int] == parse_typing(typing.Callable[[], typing.Awaitable[int]])
    >>> s = typing.TypeVar("s", int, str)
    >>> assert [int, str] == parse_typing(s)
    >>> assert [str] == parse_typing(typing_extensions.Literal["a", "b"])
    >>> assert [str] == parse_typing(typing_extensions.LiteralString)

    >>> class Demo:
    >>>     pass

    >>> assert [int] == parse_typing(typing_extensions.Annotated[int, Demo])
    >>> # Unresolved type, returned directly
    >>> from pait.util._types import _TYPING_NOT_PARSE_TYPE_SET

    >>> for i in _TYPING_NOT_PARSE_TYPE_SET:
    >>>     assert [i] == parse_typing(i)
    """
    if _is_typeddict or is_typeddict(_type):
        return [dict]

    origin: Optional[type] = getattr(_type, "__origin__", None)  # get typing.xxx's raw type
    if origin:
        if origin is Union:
            # support Union, Optional
            type_list: List[Type[Any]] = []
            for i in _type.__args__:
                type_list.extend(parse_typing((i)))
            return type_list
        elif origin is typing_extensions.Literal:
            return [str]
        elif origin in _PYTHON_ORIGIN_TYPE_SET:
            return [origin]
        arg_list: List = getattr(_type, "__args__", [])
        if arg_list:
            # support AsyncIterator, Iterator
            return parse_typing(arg_list[0])
        return [origin]
    elif _type is Generator:
        return parse_typing(_type.__args__[0])
    elif _type in _PYTHON_ORIGIN_TYPE_SET:
        return [_type]
    elif getattr(_type, "_name", "") == "Optional":
        return [type(None)]
    elif getattr(_type, "_name", "") == "LiteralString":
        return [str]
    elif hasattr(_type, "__supertype__"):
        # support NewType
        return [getattr(_type, "__supertype__")]
    elif hasattr(_type, "__constraints__"):
        # support TypeVar
        return list(getattr(_type, "__constraints__"))
    elif inspect.isclass(_type):
        return [_type]
    elif _type in _TYPING_NOT_PARSE_TYPE_SET:
        return [_type]
    else:
        raise ParseTypeError(f"Can not parse {_type} origin type")


def is_type(source_type: Type, target_type: Union[Type, object]) -> bool:
    """Determine whether the two types are consistent"""
    return bool(set(parse_typing(target_type)) & set(parse_typing(source_type)))
