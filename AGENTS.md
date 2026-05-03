# Repository Guidelines

## Project Structure & Module Organization

`pait/` contains the library code. Core decorators, models, fields, OpenAPI support, plugins, and utilities live in top-level subpackages such as `pait/field/`, `pait/model/`, `pait/openapi/`, and `pait/plugin/`. Framework integrations are under `pait/app/{flask,sanic,starlette,tornado}/`, with shared abstractions in `pait/app/base/` and framework-neutral helpers in `pait/app/any/`.

Tests are in `tests/`: `tests/test_pait/` covers core behavior and `tests/test_app/` covers framework adapters. `tests_benchmarks/` and `benchmarks/` hold benchmark code. Documentation source is in `docs/`, runnable documentation examples are in `docs_source_code/`, user-facing examples are in `example/`, and static images are in `images/` and `docs/assets/`.

## Build, Test, and Development Commands

- `pip install -r requirements/requirements-dev.txt`: install development, framework, and test dependencies.
- `pytest tests/ --capture=no`: run the main test suite configured by `pyproject.toml`.
- `pytest tests/test_app/test_flask.py --capture=no`: run one framework adapter suite; replace `flask` with `sanic`, `starlette`, or `tornado`.
- `tox -e py38-all`: run the full suite in a selected tox environment.
- `tox`: run the configured Python, framework, and Pydantic compatibility matrix.
- `coverage html`: generate an HTML coverage report after coverage-enabled runs.
- `mkdocs serve`: preview documentation locally.
- `pre-commit run --all-files`: run formatting, linting, typing, and generated requirements checks.

## Coding Style & Naming Conventions

Use Python 3.8-compatible syntax unless a tox target proves otherwise. Black and isort are configured for 120-character lines. Keep imports sorted with the Black profile. Use `snake_case` for modules, functions, variables, and test names; use `PascalCase` for classes. Preserve the existing split between framework-specific adapter code and shared base helpers.

## Testing Guidelines

Pytest is the test framework. Name test files `test_*.py` and add new tests close to the behavior being changed. For shared behavior, add coverage in `tests/test_pait/`; for adapter behavior, update the relevant `tests/test_app/test_*.py` file. Coverage is measured for `pait/` with branch coverage enabled; `pait/extra/field/stream/_multipart.py` is intentionally omitted.

## Commit & Pull Request Guidelines

Git history uses short, imperative or category-prefixed subjects such as `refactor: centralize framework path conversion`, `docs: add APIRoute...`, `Feat, add StreamFile`, and `Fix, Remove mandatory dependency...`. Prefer lowercase conventional prefixes for new commits (`fix:`, `feat:`, `docs:`, `refactor:`).

Pull requests should describe the change, list the affected frameworks or modules, link issues when relevant, and include test results. Include screenshots only for documentation or rendered UI changes.

## Security & Configuration Tips

Do not commit secrets, private keys, or local virtualenv files. Keep dependency changes in `pyproject.toml` synchronized with exported files in `requirements/` via the pre-commit hooks.

## Agent-Specific Instructions

Keep automated edits narrow and compatible with the supported framework matrix. When changing shared code in `pait/app/base/`, check at least one affected framework test and note any untested adapters. Do not rewrite generated requirement files by hand; update Poetry configuration and let the export hooks regenerate them.
