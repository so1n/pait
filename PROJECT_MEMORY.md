# pait repository memory

Repository: `/home/so1n/github/pait`

Use this memory when a future task is about the `pait` repo so the codebase does not need to be rediscovered from scratch.

## Product purpose

`pait` is a Python API helper library for multiple web frameworks. It decorates route functions and uses type hints plus Pydantic to:

- parse request parameters from query/path/header/cookie/body/form/file sources
- validate and convert values
- run dependency functions and pre/post plugins
- generate OpenAPI metadata and doc routes
- provide framework-specific test helpers and response helpers

Supported framework adapters in this repo: Flask, Sanic, Starlette, Tornado. Django is only mentioned as future work.

## Package layout

- `pait/core.py`: public `Pait` decorator implementation.
- `pait/model/core.py`: `PaitCoreModel`, route metadata, response model normalization, plugin stack construction.
- `pait/field/`: request field declarations. Important files: `http.py`, `app.py`, `resource_parse.py`.
- `pait/param_handle/`: sync/async parameter parsing and dependency execution.
- `pait/plugin/`: framework-independent plugin protocols and core plugins.
- `pait/app/`: framework adapters. Each framework has `_pait.py`, `_app_helper.py`, `_load_app.py`, `_api_route.py`, `_simple_route.py`, `_test_helper.py`, plus `adapter/`, `plugin/`, `security/`.
- `pait/openapi/`: OpenAPI model generation and doc route registration.
- `pait/g.py`, `pait/data.py`, `pait/model/config.py`: global registry, context, and one-shot config.
- `example/`: full example apps for Flask/Sanic/Starlette/Tornado.
- `docs/`: MkDocs Material documentation pages. Most code blocks include source from `docs_source_code/`.
- `docs_source_code/`: runnable documentation examples grouped by feature and framework.
- `tests/`: unit and framework adapter tests.
- `tests_benchmarks/`, `benchmarks/`: benchmark wrappers and raw-vs-Pait performance examples.

## Python environment and commands

Use the repository virtualenv as the primary Python environment:

```bash
.venv/bin/python --version
.venv/bin/python -m pytest ...
.venv/bin/python -m coverage ...
```

Current repo-local venv observed here is Python 3.8.16. Project metadata supports Python `^3.8.1`.

Avoid plain `python`/`pytest` when working in this repo unless the user explicitly asks for another environment. `pyproject.toml` also sets mypy's `python_executable = ".venv/bin/python"`.

Dependency/config notes:

- Packaging is Poetry-based with `poetry-dynamic-versioning`; exported requirement files live under `requirements/`.
- `setup.py` is legacy/static compatibility metadata and should not be treated as the source of truth for the current package version.
- `tox.ini` tests multiple Python/framework/Pydantic combinations; local targeted work should usually use `.venv/bin/python -m pytest <target>`.
- A successful quick sanity check in this workspace: `.venv/bin/python -m pytest --collect-only -q` collected 528 tests.

## Core design

The central design is framework-neutral core logic with thin framework adapters.

`Pait` wraps a route at import/registration time. It inspects the function signature, chooses sync or async param handling, creates a `PaitCoreModel`, syncs global config into it, registers it in global `pait_data`, builds a plugin chain, and returns a dispatch wrapper.

Runtime dispatch flow:

1. Framework calls decorated route wrapper.
2. `Pait.init_context` creates `ContextModel` with `BaseAppHelper`, raw args/kwargs, and `PaitCoreModel`.
3. Context is stored in a `ContextVar` via `pait.g.set_ctx`; users/plugins can call `get_ctx()`.
4. The built `main_plugin` chain runs.
5. Param handler generates route function args/kwargs from the framework request.
6. Pre plugins/post plugins wrap around the param handler depending on order.
7. Original route function receives typed Python values, not framework request maps.

Plugin stack order in `PaitCoreModel.build_plugin_stack`:

```text
pre plugins + param handler + post plugins
```

Then stack is wrapped in reverse order, so pre plugins execute before parameter generation, the param handler fills `context.args/context.kwargs`, and post plugins execute after parameter parsing but before/around the final route call.

## Parameter parsing model

`BaseRequestResourceField` in `pait/field/http.py` is both a Pait request field and a Pydantic `FieldInfo`.

Common field classes:

- `Json` and alias `Body`: request body, media type `application/json`, OpenAPI field name `body`.
- `Query`, `MultiQuery`
- `Path`
- `Header`
- `Cookie`
- `Form`, `MultiForm`
- `File`
- `Depends` in `pait/field/app.py`

Field constructor supports Pydantic constraints plus Pait extras: `raw_return`, `openapi_include`, `media_type`, `openapi_serialization`, `links`, `example`, `extra_param_list`, custom missing-value exception handler.

Important behavior:

- `BaseRequestResourceField.pre_check` verifies the framework request adapter has the requested source method and validates default/example/default_factory type early.
- `pre_load` sets `request_key`, creates and caches a `PaitModelField`, and returns `ParseResourceParamDc`.
- Runtime parse functions live in `pait/field/resource_parse.py`.
- Missing request values use field default/default_factory or raise `not_value_exception_func`.
- `raw_return=True` passes the whole source mapping/model into validation rather than selecting by key.
- `Path` rejects defaults/default_factory.

Pydantic v1/v2 differences are centralized in `pait/_pydanitc_adapter.py`; avoid direct Pydantic internals elsewhere if possible.

## Param handlers

`BaseParamHandler` in `pait/param_handle/base.py` handles pre-check and pre-load.

It discovers field type from each parameter:

- explicit default instance of `BaseField`
- request object annotations
- CBV/self annotations
- Pydantic `BaseModel` annotations

It builds `PreLoadDc` for route params and dependencies. For Pydantic models, `pait/param_handle/util.py` converts model fields into synthetic `inspect.Parameter` objects.

`ParamHandler` in `_sync.py` handles sync routes. It:

- runs `pre_depend_list`
- parses main route params
- injects CBV attributes
- supports dependency classes and sync context managers
- preserves context manager exits and raises chained errors with `raise_multiple_exc`

`AsyncParamHandler` in `_async.py` handles async routes and `sync_to_thread`. It:

- awaits coroutine parse functions/dependencies
- can run sync callables in `to_thread` when requested
- supports async and sync context managers
- calls sync or async route handlers via `run_func`

## Dependencies

`Depends.i(func)` stores a callable. `Depends.pre_check` validates the dependency signature and verifies the annotated return type matches the consuming parameter annotation. Dependency handlers can be functions, classes, sync/async context managers, or objects exposing `pait_handler`.

Security helpers are built on this: security classes create a `pait_handler` with hidden fields like `Authorization` and contribute OpenAPI security models.

## Framework adapters

`BaseAppHelper` extracts the raw request object and exposes a framework-normalized `request` adapter. Each framework provides:

- `AppHelper`: framework name, request class, CBV type, app attribute access.
- request adapter with methods `body/json/query/path/header/cookie/form/multiform/file/multiquery/stream`.
- `_load_app.py`: reads framework routes after registration and attaches path/method/openapi path metadata to `PaitCoreModel`.

`load_app(app, auto_load_route=False, override_operation_id=False, overwrite_already_exists_data=False, auto_cbv_handle=True)` is the bridge from framework route tables to OpenAPI metadata. With `auto_load_route=True`, undecorated routes can be wrapped automatically.

CBV handling is special: `load_app` or `Pait.pre_load_cbv` checks method handlers, builds class-level param rules, and injects parsed CBV fields into instance `__dict__`.

Path normalization:

- Flask/Sanic `<id>` or typed `<int:id>` becomes OpenAPI `{id}`.
- Tornado regex-style `<id>` becomes `{id}`.
- Starlette paths are already OpenAPI-like.

## Global registry and config

`pait.g` owns:

- `pait_data`: global `PaitData` route metadata registry keyed by framework app name and `pait_id`.
- `config`: global `Config`.
- `ContextVar` accessors `get_ctx()`/`set_ctx()`.

`PaitData.get_core_model` attaches real route `path`, `openapi_path`, methods, and optionally operation id. It returns a `PaitCoreProxyModel`, not the original core model, so OpenAPI can use a per-route operation id without mutating shared state unexpectedly.

`Config.init_config` is one-shot. After initialization, assigning config fields raises. `g.py` monkey-patches `config.init_config` to also sync config into already registered `PaitCoreModel`s.

`pait/extra/config.py` provides global apply functions:

- add response models or extra OpenAPI models
- block HTTP methods
- add plugins
- add pre-dependencies
- swap param handler

These can be guarded by `MatchRule` on status/group/tag/method/path or negated variants.

## OpenAPI and docs

`OpenAPI(app)` calls the framework-specific `load_app`, iterates registered `PaitCoreModel`s, unwraps proxies, parses request params and dependencies via `ParsePaitModel`, and creates `any_api` API models.

`ParsePaitModel`:

- walks extra OpenAPI models, dependencies, and route function signature
- groups fields by HTTP source (`query`, `path`, `header`, `body`, etc.)
- converts single fields and Pydantic models into generated Pydantic models for OpenAPI request bodies/parameters
- detects security dependencies and adds security models

`pait/openapi/doc_route.py` adds `/openapi.json` and UI routes for Swagger/Redoc/RapiDoc/Elements using `any_api.openapi.web_ui`. It protects docs with optional `pin_code` and uses `TemplateContext` for template variables.

## Response models

`pait/model/response.py` wraps `any_api` response model classes and adds default/example generation.

If `response_model_list` contains a Pydantic `BaseModel`, `PaitCoreModel.add_response_model_list` converts it to a `JsonResponseModel` subclass via `create_json_response_model`.

Default response examples are generated from Pydantic defaults, `example` metadata, enum first values, or configured default values.

## Plugin system

`PluginProtocol` is a chain node. Users never instantiate plugins directly; they call `SomePlugin.build(...)`, which returns `PluginManager`.

`PluginManager` keeps plugin class plus kwargs and isolates per-route plugin instances.

Hooks:

- `pre_check_hook`: runs when plugin is added, unless `PAIT_IGNORE_PRE_CHECK` is set.
- `pre_load_hook`: runs during `build_plugin_stack`, can prepare cached data from route metadata.
- `__call__`: runtime chain entry.

Core plugins:

- `CheckJsonRespPlugin`: validates JSON response content against selected `JsonResponseModel`.
- `AutoCompleteJsonRespPlugin`: merges route result into default response shape.
- `MockPluginProtocol`: skips route function and returns generated mock response or file response.
- `UnifiedResponsePlugin`: wraps raw return value into framework-specific response objects. Actual framework response generation is in `pait/app/<framework>/plugin/`.
- `CacheResponsePlugin`: Redis-based cache around route result. Requires `decode_responses=True`, can use app attribute or explicit Redis client, and can merge params into cache key. Does not support file responses.
- `RequiredPlugin`: parameter dependency validation after parsing.
- `AtMostOneOfPlugin`: mutually exclusive parameter validation after parsing.

Extra field params such as `RequiredExtraParam`, `RequiredGroupExtraParam`, `AtMostOneOfExtraParam`, `CacheRespExtraParam` live on field `extra_param_list` and are consumed by plugin `pre_load_hook`.

## Security design

Base security classes live under `pait/app/base/security/`. Framework-specific security modules mainly provide exception classes/integration.

Security classes generate hidden Pait fields and `pait_handler` functions, so they plug into normal `Depends` handling and OpenAPI parsing.

Important classes:

- API key: query/header/cookie via `BaseAPIKey`.
- HTTP Basic/Bearer/Digest via `BaseHTTPBasic`, `BaseHTTPBearer`, `BaseHTTPDigest`.
- OAuth2 password bearer and password form helpers in `oauth2.py`.

OAuth2 route binding uses `BaseOAuth2PasswordBearer.with_route(route)` and listens to `PaitCoreModel` changes to update `tokenUrl`.

## API route abstraction

`pait/app/base/api_route.py` defines `BaseAPIRoute`, `RouteDc`, `CbvRouteDc`.

This is a framework-neutral route collection abstraction:

- collect routes via `.get()`, `.post()`, `.add_api_route()`, `.add_cbv_route()`
- include sub-routes via `include_sub_route()` or `<<`
- merge parent/child Pait params with append semantics
- framework-specific `_api_route.py` injects collected routes into real apps

This is separate from native framework routing and should preserve framework-specific `framework_extra_param`.

## Docs and examples

Documentation structure:

- `mkdocs.yml` defines the documentation nav. Add new public docs there if adding a new page.
- Docs use MkDocs Material, admonitions, tabs, and snippet includes like `--8<-- "docs_source_code/...py"`.
- Feature docs are under `docs/` by topic: introduction, field/type/depend/exception, Pait decorator, APIRoute, OpenAPI/security, TestHelper, plugins, config, other.
- Keep docs prose practical and tie behavior back to one of the four framework tabs when framework usage differs.

Documentation example conventions:

- `docs_source_code/` examples are intended to be executable or testable, not pseudocode.
- Most feature examples are duplicated per framework (`flask_...`, `sanic_...`, `starlette_...`, `tornado_...`). When behavior is framework-neutral, keep examples parallel except for imports, response types, app creation, and route registration.
- The docs normally show the route function, `@pait(...)`, field declarations, response model, app registration, and sometimes doc route registration.
- Use `Json.t(...)` / `Depends.t(...)` when docs want type-checker-friendly return typing; use `.i(...)` for concise runtime examples.
- Examples commonly define Pydantic response models via `JsonResponseModel` subclasses or pass Pydantic `BaseModel` classes directly where supported.

Full example app conventions:

- `example/common/` holds shared request/response models, dependencies, tags, security helpers, and utilities.
- `example/<framework>_example/` mirrors the same feature routes across frameworks: `field_route.py`, `depend_route.py`, `response_route.py`, `plugin_route.py`, `security_route.py`, `openapi_example.py`, `api_route.py`, and `main_example.py`.
- `main_example.py` is an integration hub that imports feature routes, builds grouped `Pait` instances, registers doc routes, and creates the framework app.
- Keep example behavior aligned across frameworks because `tests/test_app/base_api_test.py` reuses shared assertions against different adapters.

## Testing and development

Dependency management:

- project metadata in `pyproject.toml` using Poetry and `poetry-dynamic-versioning`
- exported requirement files under `requirements/`
- runtime dependency baseline includes `any-api` and Pydantic

Test organization:

- `tests/test_pait/`: framework-independent unit tests for core, data, field, param handling, model, OpenAPI parser, plugin, security, utility behavior.
- `tests/test_app/`: framework adapter and integration tests for Flask/Sanic/Starlette/Tornado plus protocol/path/helper tests.
- `tests/test_app/base_api_test.py`, `base_openapi_test.py`, and `base_doc_example_test.py` hold reusable assertions shared by framework-specific test files.
- `tests/conftest.py` contains fixtures/context managers such as `enable_plugin`, `enable_resp_model`, and `fixture_loop`.
- `tests_benchmarks/` dynamically wraps framework tests with pytest-benchmark.

Test writing style:

- Use pytest classes like `TestPaitCore`, `TestStarlette`, etc.; test methods are plain methods with fixtures as arguments.
- Prefer exact behavioral assertions over loose smoke tests. Many tests assert exact dicts, OpenAPI schema fragments, route paths, status codes, and error messages.
- For framework integration tests, construct a framework test client fixture and pass route functions to the framework-specific `TestHelper`.
- Prefer shared `BaseTest` helper methods when adding the same feature across frameworks.
- When mutating route metadata or plugins inside a test, use `enable_plugin` / `enable_resp_model` so original `PaitCoreModel` state is restored.
- Starlette tests may need event-loop repair because other framework tests can close the default loop.
- Flask tests often need to ignore auto-added methods like `HEAD` or `OPTIONS` when auto-discovering methods.
- Redis-backed cache tests assume a Redis client/service is available; be explicit if a new test depends on Redis.

Common commands:

```bash
.venv/bin/python -m pytest tests/test_pait/test_field.py
.venv/bin/python -m pytest tests/test_app/test_starlette.py::TestStarlette::test_post
.venv/bin/python -m pytest --collect-only -q
.venv/bin/python -m coverage run -m pytest tests/
.venv/bin/python -m coverage report
tox
tox -e py38-pydantic-v110
```

CI in `.github/workflows/python-package.yml` runs Python 3.8-3.11, flake8, Redis, and `coverage run -m pytest tests/`.

Examples can be run directly:

```bash
.venv/bin/python example/starlette_example/main_example.py
.venv/bin/python example/flask_example/main_example.py
.venv/bin/python example/sanic_example/main_example.py
.venv/bin/python example/tornado_example/main_example.py
```

Most example apps use port 8000. Redis-backed examples/tests need Redis.

## Code style and risk notes

- Keep framework-neutral logic in `pait/core.py`, `model`, `field`, `param_handle`, `plugin`, `openapi`.
- Put framework-specific behavior in `pait/app/<framework>/...`.
- Keep imports explicit and grouped by stdlib / third-party / local; use isort's black profile.
- Line length is 120. Black/isort are configured in `pyproject.toml`; `.flake8` also uses 120 and ignores `F401,W503,E203,E701`.
- Public/internal APIs are typed heavily. New functions in `pait/` should have annotations because mypy has `disallow_untyped_defs = true`.
- Prefer small framework-neutral helpers in `pait/` and thin framework-specific wrappers under `pait/app/<framework>/`.
- Use `TYPE_CHECKING` imports to avoid runtime dependency cycles.
- Comments are usually short and explain why a compatibility or lifecycle detail exists. Avoid broad rewrites or style-only churn.
- Do not bypass `_pydanitc_adapter.py` for Pydantic v1/v2 compatibility.
- Be careful when changing `PaitCoreModel.build_plugin_stack`; plugin execution order is central.
- Be careful with `Config.init_config`; it is intentionally one-shot and synchronized to existing core models.
- Do not mutate `PaitCoreProxyModel` thinking it is the source model; unwrap with `PaitCoreProxyModel.get_core_model` when needed.
- Tests often rely on exact error messages and tip exception formatting.
- Backward compatibility matters: there are old aliases like `PaitResponseModel`, deprecated params, and legacy-compatible extra kwargs paths.
- Many checks happen at decorator/build time to fail early, not at request time.
- `load_app(auto_load_route=True)` may decorate previously undecorated framework handlers; preserve route table replacement logic if editing.
- `get_func_sig` caches signatures and resolves postponed annotations; invalidating or bypassing it can break annotation handling.
- The project values broad framework/version compatibility over local simplification.

## First files to inspect for future changes

Start with these depending on task:

- route decorator/runtime behavior: `pait/core.py`, `pait/model/core.py`, `pait/param_handle/base.py`, `_sync.py`, `_async.py`
- request fields/validation: `pait/field/http.py`, `pait/field/resource_parse.py`, `pait/_pydanitc_adapter.py`
- framework route loading: `pait/app/<framework>/_load_app.py`, `_app_helper.py`, `adapter/request.py`
- OpenAPI/doc behavior: `pait/openapi/openapi.py`, `pait/openapi/doc_route.py`
- plugins: `pait/plugin/base.py` plus the specific plugin file and framework wrapper under `pait/app/<framework>/plugin/`
- tests: targeted file under `tests/test_pait/` or `tests/test_app/`, plus `tests/conftest.py`
