from typing import Type

import aiofiles  # type: ignore

from pait.app.base import BaseAppHelper
from pait.core import Pait as _Pait

from ._app_helper import AppHelper

__all__ = ["pait", "Pait"]


class Pait(_Pait):
    app_helper_class: "Type[BaseAppHelper]" = AppHelper


pait = Pait()
