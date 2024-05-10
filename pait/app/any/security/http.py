from typing import Type

from pait.app.base.security.http import BaseHTTPBasic, BaseHTTPBearer, BaseHTTPDigest, HTTPBasicCredentials

from .util import get_security

__all__ = ["HTTPBasic", "HTTPDigest", "HTTPBearer", "HTTPBasicCredentials"]

HTTPBasic: Type[BaseHTTPBasic] = get_security("HTTPBasic", "http")
HTTPDigest: Type[BaseHTTPDigest] = get_security("HTTPDigest", "http")
HTTPBearer: Type[BaseHTTPBearer] = get_security("HTTPBearer", "http")
