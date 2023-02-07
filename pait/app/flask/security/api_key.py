from abc import ABCMeta

from pait.app.base.security.api_key import BaseAPIKey
from pait.app.base.security.api_key import api_key as _api_key
from pait.util import partial_wrapper

from .util import GetException


class APIKey(GetException, BaseAPIKey, metaclass=ABCMeta):
    pass


api_key = partial_wrapper(_api_key, api_key_class=APIKey)
