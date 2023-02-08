from importlib import import_module
from typing import Type

from pait.app.auto_load_app import auto_load_app_class
from pait.app.base.security.api_key import BaseAPIKey

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower() + ".security.api_key"
APIKey: Type[BaseAPIKey] = getattr(import_module(pait_app_path), "APIKey")
