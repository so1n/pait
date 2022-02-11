from .build_benchmarks import build_test

build_test("starlette", ["client", "base_test"], locals())
