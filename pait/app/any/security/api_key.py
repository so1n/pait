from importlib import import_module
from typing import Callable, Optional, Type

from pait.app.any.util import base_call_func
from pait.app.auto_load_app import auto_load_app_class
from pait.app.base.security.api_key import APIKEY_FIELD_TYPE
from pait.app.base.security.api_key import APIkey as BaseAPIKey

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower() + ".security.api_key"
APIKey: Type[BaseAPIKey] = getattr(import_module(pait_app_path), "APIKey")


def api_key(
    *,
    name: str,
    field: APIKEY_FIELD_TYPE,
    verify_api_key_callable: Callable[[str], bool],
    security_name: Optional[str] = None,
    api_key_class: Type[BaseAPIKey] = APIKey,
) -> BaseAPIKey:
    return base_call_func(
        "api_key",
        name=name,
        module_name="security.api_key",
        api_key_class=api_key_class,
        field=field,
        verify_api_key_callable=verify_api_key_callable,
        security_name=security_name,
    )
