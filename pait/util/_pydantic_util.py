from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from pydantic.schema import (
    default_ref_template,
    get_flat_models_from_model,
    get_model,
    get_model_name_map,
    get_schema_ref,
    model_process_schema,
)

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic.dataclasses import Dataclass
    from pydantic.schema import TypeModelSet


global_flat_model_set: "TypeModelSet" = set()


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
    global global_flat_model_set
    model = get_model(model)
    flat_models = get_flat_models_from_model(model)
    global_flat_model_set = global_flat_model_set | flat_models
    model_name_map = get_model_name_map(global_flat_model_set)
    model_name = model_name_map[model]
    m_schema, m_definitions, nested_models = model_process_schema(
        model, by_alias=by_alias, model_name_map=model_name_map, ref_prefix=ref_prefix, ref_template=ref_template
    )
    if model_name in nested_models:
        # model_name is in Nested models, it has circular references
        m_definitions[model_name] = m_schema
        m_schema = get_schema_ref(model_name, ref_prefix, ref_template, False)
    if m_definitions:
        m_schema.update({"definitions": m_definitions})
    return m_schema
