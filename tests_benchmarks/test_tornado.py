import importlib
import sys
from typing import Any

from pytest_benchmark.fixture import BenchmarkFixture

from pait.app.auto_load_app import app_list

for i in app_list:
    sys.modules.pop(i, None)
app_name = "tornado"

app_test_module = importlib.import_module(f"tests.test_app.test_{app_name}")
for app_test_class_name in [""]:
    app_test_class_name = f"Test{app_name.title()}{app_test_class_name}"
    app_test_class = getattr(app_test_module, app_test_class_name)

    benchmark_class_method_dict = {}

    for unittest_name in dir(app_test_class):
        if not unittest_name.startswith("test"):
            continue

        raw_unittest_method = getattr(app_test_class, unittest_name)

        def _(class_: Any, fn: Any) -> Any:
            """Prevent for loop closure problems"""

            def test_benchmarks(self: Any, benchmark: BenchmarkFixture) -> Any:
                instance = class_(methodName="run")
                # There is no need for anything else at the moment, just call the setUp method
                instance.setUp()
                # real benchmark
                benchmark(getattr(instance, fn.__name__))

            benchmark_class_method_dict[fn.__name__ + "_benchmarks"] = test_benchmarks

        _(app_test_class, raw_unittest_method)
        locals()[app_test_class_name] = type(app_test_class_name, (object,), benchmark_class_method_dict)
    locals().pop(app_test_class, None)
