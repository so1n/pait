from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple, Type, Union

from pydantic import create_model
from pydantic.schema import (
    default_ref_template,
    get_flat_models_from_model,
    get_long_model_name,
    get_model,
    get_schema_ref,
    model_process_schema,
    normalize_name,
)

if TYPE_CHECKING:
    from pydantic import BaseConfig, BaseModel
    from pydantic.dataclasses import Dataclass
    from pydantic.schema import TypeModelOrEnum, TypeModelSet


global_name_model_map = {}
global_conflicting_names: Set[str] = set()


def get_model_global_name(model: "TypeModelOrEnum") -> str:
    return pait_get_model_name_map({model})[model]


def pait_get_model_name_map(unique_models: "TypeModelSet") -> Dict["TypeModelOrEnum", str]:
    """
    Process a set of models and generate unique names for them to be used as keys in the JSON Schema
    definitions. By default the names are the same as the class name. But if two models in different Python



    modules have the same name (e.g. "users.Model" and "items.Model"), the generated names will be
    based on the Python module path for those conflicting models to prevent name collisions.

    :param unique_models: a Python set of models
    :return: dict mapping models to names
    """
    global global_name_model_map
    global global_conflicting_names

    for model in unique_models:
        model_name = normalize_name(model.__name__)
        if model_name in global_conflicting_names:
            model_name = get_long_model_name(model)
            global_name_model_map[model_name] = model
        elif model_name in global_name_model_map:
            global_conflicting_names.add(model_name)
            conflicting_model = global_name_model_map.pop(model_name)
            global_name_model_map[get_long_model_name(conflicting_model)] = conflicting_model
            global_name_model_map[get_long_model_name(model)] = model
        else:
            global_name_model_map[model_name] = model
    return {v: k for k, v in global_name_model_map.items()}


def pait_model_schema(
    model: Union[Type["BaseModel"], Type["Dataclass"]],
    by_alias: bool = True,
    ref_prefix: Optional[str] = None,
    ref_template: str = default_ref_template,
) -> Dict[str, Any]:
    """
    Generate a JSON Schema for one model. With all the sub-models defined in the ``definitions`` top-level
    JSON key.

    :param model: a Pydantic model (a class that inherits from BaseModel)
    :param by_alias: generate the schemas using the aliases defined, if any
    :param ref_prefix: the JSON Pointer prefix for schema references with ``$ref``, if None, will be set to the
      default of ``#/definitions/``. Update it if you want the schemas to reference the definitions somewhere
      else, e.g. for OpenAPI use ``#/components/schemas/``. The resulting generated schemas will still be at the
      top-level key ``definitions``, so you can extract them from there. But all the references will have the set
      prefix.
    :param ref_template: Use a ``string.format()`` template for ``$ref`` instead of a prefix. This can be useful for
      references that cannot be represented by ``ref_prefix`` such as a definition stored in another file. For a
      sibling json file in a ``/schemas`` directory use ``"/schemas/${model}.json#"``.
    :return: dict with the JSON Schema for the passed ``model``
    """
    model = get_model(model)
    flat_models = get_flat_models_from_model(model)
    model_name_map = pait_get_model_name_map(flat_models)
    model_name = model_name_map[model]
    m_schema, m_definitions, nested_models = model_process_schema(
        model, by_alias=by_alias, model_name_map=model_name_map, ref_prefix=ref_prefix, ref_template=ref_template
    )
    if model_name in nested_models:
        # model_name is in Nested models, it has circular references
        m_definitions[model_name] = m_schema  # pragma: no cover
        m_schema = get_schema_ref(model_name, ref_prefix, ref_template, False)  # pragma: no cover
    if m_definitions:
        m_schema.update({"definitions": m_definitions})
    return m_schema


def create_pydantic_model(
    annotation_dict: Dict[str, Tuple[Type, Any]],
    class_name: str = "DynamicModel",
    pydantic_config: Type["BaseConfig"] = None,
    pydantic_base: Type["BaseModel"] = None,
    pydantic_module: str = "pydantic.main",
    pydantic_validators: Dict[str, classmethod] = None,
) -> Type["BaseModel"]:
    """pydantic self.pait_response_model helper
    if use create_model('DynamicModel', **annotation_dict), mypy will tip error
    """
    return create_model(
        class_name,
        __config__=pydantic_config,
        __base__=pydantic_base,
        __module__=pydantic_module,
        __validators__=pydantic_validators,
        **annotation_dict,
    )
