from typing import Any, Callable, Optional


class BaseField:
    def __init__(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None,
            fix_key: bool = False
    ):
        self.key = key
        self.default = default
        self.fix_key = fix_key


class Body(BaseField):
    pass


class Cookie(BaseField):
    pass


class File(BaseField):
    pass


class Form(BaseField):
    pass


class Header(BaseField):
    pass


class Path(BaseField):
    pass


class Query(BaseField):
    pass


class Depends(object):
    def __init__(self, func: Callable):
        self.func: Callable = func
