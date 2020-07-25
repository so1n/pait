from typing import Any, Optional


class BaseField:
    def __init__(
            self,
            key: Optional[str] = None,
            default: Optional[Any] = None
    ):
        self.key = key
        self.default = default


class Body(BaseField):
    pass


class Cookie(BaseField):
    pass


class File(BaseField):
    pass


class From(BaseField):
    pass


class Header(BaseField):
    pass


class Query(BaseField):
    pass
