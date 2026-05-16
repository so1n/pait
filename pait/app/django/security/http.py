from pait.app.base.security.http import BaseHTTPBasic, BaseHTTPBearer, BaseHTTPDigest, HTTPBasicCredentials

from .util import GetException

__all__ = ["HTTPBasic", "HTTPDigest", "HTTPBearer", "HTTPBasicCredentials"]


class HTTPBasic(GetException, BaseHTTPBasic):
    pass


class HTTPDigest(GetException, BaseHTTPDigest):
    pass


class HTTPBearer(GetException, BaseHTTPBearer):
    pass
