import sys

# copy from https://github.com/agronholm/typeguard/blob/master/src/typeguard/__init__.py#L64
if sys.version_info >= (3, 10):
    from typing import ParamSpec  # pragma: no cover
    from typing import is_typeddict  # pragma: no cover
    from typing import Literal
else:
    from typing_extensions import ParamSpec  # type: ignore
    from typing_extensions import Literal

    _typed_dict_meta_types = ()
    if sys.version_info >= (3, 8):
        from typing import _TypedDictMeta  # pragma: no cover

        _typed_dict_meta_types += (_TypedDictMeta,)  # pragma: no cover

    try:
        from typing_extensions import _TypedDictMeta  # type: ignore

        _typed_dict_meta_types += (_TypedDictMeta,)  # type: ignore
    except ImportError:  # pragma: no cover
        pass

    def is_typeddict(tp) -> bool:  # type: ignore
        return isinstance(tp, _typed_dict_meta_types)


__all__ = ["ParamSpec", "Literal", "is_typeddict"]
