from collections.abc import AsyncIterator, Iterator
from typing import Any, List, Optional, Set, Type, Union, _GenericAlias  # type: ignore

from pait.exceptions import ParseTypeError

_CAN_JSON_TYPE_SET: Set[Optional[type]] = {bool, dict, float, int, list, str, tuple, type(None), None}


def parse_typing(_type: Any) -> Union[List[Type[Any]], Type]:
    """
    parse typing.type to Python.type
    >>> from typing import Dict, Optional
    >>> assert dict is parse_typing(dict)
    >>> assert list is parse_typing(List)
    >>> assert dict is parse_typing(Dict)
    >>> assert dict in set(parse_typing(Optional[Dict]))
    >>> assert None in set(parse_typing(Optional[Dict]))
    >>> assert dict in set(parse_typing(Optional[dict]))
    >>> assert None in set(parse_typing(Optional[dict]))
    >>> assert dict is parse_typing(Union[dict])
    >>> assert dict is parse_typing(Union[Dict])
    >>> assert dict is parse_typing(Union[Dict[str, Any]])
    """
    if isinstance(_type, _GenericAlias):
        # support typing.xxx
        origin: type = _type.__origin__  # get typing.xxx's raw type
        if origin is Union:
            # support Union, Optional
            type_list: List[Type[Any]] = []
            for i in _type.__args__:
                if isinstance(i, list):
                    for j in i:
                        value: Union[List[Type[Any]], Type] = parse_typing(j)
                        if isinstance(value, list):
                            type_list.extend(value)
                        else:
                            type_list.append(value)
                else:
                    value = parse_typing(i)
                    if isinstance(value, list):
                        type_list.extend(value)
                    else:
                        type_list.append(value)
            return type_list
        elif origin in (AsyncIterator, Iterator):
            # support AsyncIterator, Iterator
            return parse_typing(_type.__args__[0])
        return origin
    elif _type in _CAN_JSON_TYPE_SET:
        return _type
    else:
        raise ParseTypeError(f"Can not parse {_type} origin type")


def is_type(source_type: Type, target_type: Union[Type, object]) -> bool:
    """Determine whether the two types are consistent"""
    parse_source_type: Union[List[Type], Type] = parse_typing(source_type)
    if not isinstance(parse_source_type, list):
        parse_source_type = [parse_source_type]

    parse_target_type: Union[List[Type], Type] = parse_typing(target_type)
    if not isinstance(parse_target_type, list):
        parse_target_type = [parse_target_type]
    return bool(set(parse_target_type) & set(parse_source_type))
