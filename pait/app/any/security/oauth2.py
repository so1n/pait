from importlib import import_module
from typing import Type

from pait.app.auto_load_app import auto_load_app_class
from pait.app.base.security.oauth2 import (
    BaseOAuth2PasswordBearer,
    BaseOAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFrom,
    OAuth2PasswordRequestFromStrict,
)

__all__ = [
    "OAuth2PasswordBearer",
    "OAuth2PasswordRequestFrom",
    "OAuth2PasswordRequestFromStrict",
    "BaseOAuth2PasswordRequestFrom",
]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower() + ".security.oauth2"
OAuth2PasswordBearer: Type[BaseOAuth2PasswordBearer] = getattr(import_module(pait_app_path), "OAuth2PasswordBearer")
