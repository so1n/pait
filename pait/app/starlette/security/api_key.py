from abc import ABCMeta
from typing import Callable, Optional

from starlette.exceptions import HTTPException

from pait.app.base.security.api_key import APIKEY_FIELD_TYPE, APIkey
from pait.app.base.security.api_key import api_key as _api_key


class StarletteAPIkey(APIkey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        return HTTPException(status_code=status_code, detail=message)


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
) -> APIkey:
    return _api_key(
        name=name,
        api_key_class=StarletteAPIkey,
        field=field,
        verify_api_key_callable=verify_api_key_callable,
        security_name=security_name,
    )
