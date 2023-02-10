from importlib import import_module
from typing import Type

from pait.app.auto_load_app import auto_load_app_class
from pait.app.base.security.http import BaseHTTPBasic, BaseHTTPBearer, BaseHTTPDigest, HTTPBasicCredentials

__all__ = ["HTTPBasic", "HTTPDigest", "HTTPBearer", "HTTPBasicCredentials"]

pait_app_path: str = "pait.app." + auto_load_app_class().__name__.lower() + ".security.http"
HTTPBasic: Type[BaseHTTPBasic] = getattr(import_module(pait_app_path), "HTTPBasic")
HTTPDigest: Type[BaseHTTPDigest] = getattr(import_module(pait_app_path), "HTTPDigest")
HTTPBearer: Type[BaseHTTPBearer] = getattr(import_module(pait_app_path), "HTTPBearer")
