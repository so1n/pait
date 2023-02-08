from pait.app.base.security.api_key import BaseAPIKey

from .util import GetException


class APIKey(GetException, BaseAPIKey):
    pass
