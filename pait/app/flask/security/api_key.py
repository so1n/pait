from abc import ABCMeta
from typing import Callable, Optional

from werkzeug.exceptions import HTTPException

from pait.app.base.security.api_key import APIKEY_FIELD_TYPE, APIkey
from pait.app.base.security.api_key import api_key as _api_key


class FlaskAPIkey(APIkey, metaclass=ABCMeta):
    @classmethod
    def get_exception(cls, *, status_code: int, message: str) -> Exception:
        exc = HTTPException(description=message)
        exc.code = status_code
        return exc


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
) -> APIkey:
    return _api_key(
        name=name,
        api_key_class=FlaskAPIkey,
        field=field,
        verify_api_key_callable=verify_api_key_callable,
        security_name=security_name,
    )
