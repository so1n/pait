from typing import Any, Optional


class BaseField:
    def __init__(
            self,
            default: Optional[Any] = None
    ):
        self.default = default


class _KeyField(BaseField):
    def __init__(
            self,
            key: str,
            default: Optional[Any] = None
    ):
        self.header_key: str = key
        super().__init__(default)


class Body(BaseField):
    pass


class Cookie(_KeyField):
    pass


class File(BaseField):
    pass


class From(BaseField):
    pass


class Header(_KeyField):
    pass


class Query(BaseField):
    pass
