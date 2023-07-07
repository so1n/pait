import importlib
import inspect
import sys
from typing import Any, Callable, Generator

import pytest
from pytest_benchmark.fixture import BenchmarkFixture
from pytest_mock import MockFixture

from pait.app.auto_load_app import app_list


class Demo(object):
    pass


@pytest.fixture(autouse=True)
def client() -> Generator[Demo, None, None]:
    yield Demo()


@pytest.fixture(autouse=True)
def base_test() -> Generator[Demo, None, None]:
    yield Demo()


def build_test(app_name: str, fixture_column_list: list, local_dict: dict, class_: type = object) -> None:
    for i in app_list:
        sys.modules.pop(i, None)
    app_test_module = importlib.import_module(f"tests.test_app.test_{app_name}")
    for app_test_class_name in [""]:
        app_test_class_name = f"Test{app_name.title()}{app_test_class_name}"
        app_test_class = getattr(app_test_module, app_test_class_name)

        local_dict["client"] = client
        local_dict["base_test"] = base_test

        # set fixture
        for column in fixture_column_list:
            local_dict[column] = getattr(app_test_module, column)

        benchmark_class_method_dict = {}

        for unittest_name in dir(app_test_class):
            if not unittest_name.startswith("test"):
                continue

            raw_unittest_method = getattr(app_test_class, unittest_name)

            def _(fn: Callable) -> None:
                """Prevent for loop closure problems"""
                new_unitest_method_name = fn.__name__ + "_benchmarks"
                benchmark_class_method_dict["_" + new_unitest_method_name] = fn

                def test_benchmarks(
                    self: Any, benchmark: BenchmarkFixture, client: Any, base_test: Any, mocker: MockFixture
                ) -> None:
                    # The parameters that the function may receive
                    raw_param_dict: dict = {"client": client, "base_test": base_test, "mocker": mocker}

                    # Generate the parameters required by the function based on the function signature
                    func_param_dict: dict = {}
                    for k in inspect.signature(fn).parameters.keys():
                        if k not in raw_param_dict:
                            continue
                        func_param_dict[k] = raw_param_dict[k]

                    # real benchmark
                    benchmark(getattr(self, "_" + new_unitest_method_name), **func_param_dict)

                benchmark_class_method_dict[new_unitest_method_name] = test_benchmarks

            _(raw_unittest_method)
            local_dict[app_test_class_name] = type(app_test_class_name, (class_,), benchmark_class_method_dict)
