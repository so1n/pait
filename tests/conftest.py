from contextlib import contextmanager
from typing import Generator

from pait.app.base import BaseTestHelper
from pait.g import config

config.init_config(block_http_method_set={"HEAD", "OPTIONS"})


@contextmanager
def enable_mock(test_helper: BaseTestHelper) -> Generator[None, None, None]:
    try:
        test_helper.pait_core_model.pait_func = test_helper.pait_core_model.return_mock_response
        yield
    finally:
        test_helper.pait_core_model.pait_func = test_helper.pait_core_model.func
