### 0.8.x[Future]
- 1 Add a user-friendly doc ui
- 2 Plugin Panel


### 0.7.4.3[Now]
- Fix: gen BaseModel param

### 0.7.4.2
- Fix: OpenAPI _field_list_2_request_body not use _replace_pydantic_definitions method
- Fix: config.init_config i18n param not enable
### 0.7.4.1
- Feature: Support Enum Type in response
- Refactor: check_field_type core func is_type -> create_pydantic_model
### 0.7.4
Improve the interaction of md documents and increase the functionality of existing plug-ins

- Style: Change md doc style
- Feature: Md Support i18n and Request Param table support display example and other column
- Feature: Friendly exc design
- Feature: Check Field's default,example and default_factory value type when program start
- Refactor: Refactor mock response plugin
- Feature: Add auto complete json plugin

### 0.7.3
Core architecture modification, support for plug-in mechanism

- Feature: Support create sub pait
- Feature: Support tag model
- Feature: Core support plugin and change param_handle to plugin
- Feature: mock response plugin and response model add is_core flag
- Feature: check json response plugin
- Feature: `required`&`at most one of` plugin
- Fix: fix not support default_factory

### 0.7.2
Improve openapi support (except for the security part);
Improve Response type;
Improve TestHelper;
Improve parsing speed

- Fix: fix openapi init check and fix can not found real field property in basemodel
- Fix: fix sanic load app bug
- Feature: Api Doc support schema param
- Feature: TestHelper add json method and limit auto select http method
- Feature: remove PaitBaseModel and support parse BaseModel pait.field
- Feature: openapi support all pait.field
- Feature: openapi schema support same model name(auto gen long name)
- Feature: add more response model and mock support mutil response model
- Feature: support openapi links
- Feature: Change param handler and improve parsing speed
- Refactor: TestHelper access_response
- Refactor: pait.app.base
- Refactor: pait func to pait obj
- Refactor: example and test
### 0.7.1
Emergency fix version

- Fix: fix ignore field.Depends parse in get_parameter_list_from_class
### 0.7

Simplify and optimize code logic and reduce code coupling.
Support for closure scenarios and the addition of several parameters to @pait()

- Fix: Fix, Resolve the key mismatch between Field.alias and request value
- Fix: fix incompatibility with different fields having the same alias
- Feature: Refactor model.config and model.core, @pait() add param `enable_mock_response`
- Feature: Laze property support auto use class
- Feature: Support closure cbv
- Feature: Support for user-defined Pydantic BaseModel Config (for pait dynamically produced Pydantic BaseModel based on function parameters)
- Feature: Api doc route support https and use @pait()
### 0.6.3
- Feature: Support Pre Depend

### 0.6.2
- Feature: Support mock value anc mock fn value by Field.example attr
- Feature: Support config json encoder
- Fix: fix pydantic schema not support default value is None
- Fix: fix gen_example_dict_from_schema gen enum value bug
- Fix: fix pydantic schema default desc is null and snaic openapi bug
- Refactor: refactor param_handler

### 0.6.1
- Fix: can not raise real exc;refactor raise_and_tip -> gen_tip_exc
- Feature: modify test client helper diff_response logic
- Feature: example json value support Python TypeHints:Any

### 0.6.0
 - Feature: add param required check
 - Feature: support DynamicModel config
 - Feature: add global block http method
 - Feature: add check response in test helper
 - Refactor: core structure
### 0.5.9
 - Feature: mock response
 - Feature: test client helper
### 0.5.8.2
 - Feature: global config support not call `setatter` in runtime
 - Feature: support set customer name
 - Fix, fix md doc display other filed param
### 0.5.8.1
 - Feature: openapi support RequestBody schema
 - Remove: remove pait&json&yaml doc
### 0.5.8
 - Fix: refactor circular reference
### 0.5.7
 - Feature: add global config
 - Fix: fix `param_handle` can not parse single field bug
 - Fix: support update json type default value
### 0.5.6
 - Fix: fix python3.8 annotation
 - Fix: single filed not pydantic filed info

### 0.5.5
 - Fix: update requirements and resolve pydantic`s CVE-2021-29510
 - Fix: sanic new version bug
 - Fix: new version pait.app pait func bug

### 0.5.4
 - Feature: support summary column
 - Feature: doc module support project name
 - Feature: support redoc ui route
 - Feature: support swagger ui route
 - Refactor: pait.api_doc & pait.app

### 0.5.3
 - Test: add param handle test
 - Test: add util test
 - Feature: support postponed annotations
 - Feature: load_app support return pait data
 - Feature: add multi field and add lazyproperty
 - Feature: support tornado, sanic
### 0.5.2
 - Test: add pait param verify test
 - Feature: BaseField add raw_return
 - Feature: add create_pydantic_model func
 - Feature: add BaseField inherit limit
 - Refactor: refactor app helper
 - Fix: fix param_handle bug
 - Example: add example Response

### 0.5.1
 - Style: add mypy check
 - Feature: filed support mypy check
 - Feature: support openapi allOf

### 0.5.0
 - Refactor: New design&program architecture
 - Feature: add interface info(life cycle, author, group, desc....)
 - Feature: add auto load app
 - Feature: add PaitBaseModel
 - Feature: add markdown/json/yaml api doc
 - Feature: api doc support openapi
### 0.4.1
 - Feature: add raise error response

## 0.4
 - Feature: support Dependencies

### 0.3.3
 - Feature: support cbv error tip

### 0.3.2
 - Future: support cbv class attribute

### 0.3.1
 - Feature: add more field

## 0.2
 - Feature: support cbv

## 0.1.5
 - Feature: support flask type checking and parameter type conversion

## 0.1
 - description: The first version
 - Feature: support starletter type checking and parameter type conversion
