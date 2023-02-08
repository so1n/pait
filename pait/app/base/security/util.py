from pait.field import BaseField


def set_and_check_field(pait_field: BaseField, alias: str, not_authenticated_exc: Exception) -> None:
    if pait_field.alias is not None:
        raise ValueError("Custom alias parameters are not allowed")
    if pait_field.not_value_exception is not None:
        raise ValueError("Custom not_value_exception parameters are not allowed")
    pait_field.set_alias(alias)
    pait_field.not_value_exception = not_authenticated_exc
