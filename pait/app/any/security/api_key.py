from typing import Type

from pait.app.base.security.api_key import BaseAPIKey

from .util import get_security

APIKey: Type[BaseAPIKey] = get_security("APIKey", "api_key")
