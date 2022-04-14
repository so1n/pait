import re
from contextvars import ContextVar, Token
from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

__all__ = ["i18n_local", "change_local", "join_i18n", "I18n", "I18nContext", "I18nTypedDict", "i18n_config_dict"]
I18nTypedDict = TypedDict("I18nTypedDict", {"en": str, "zh-cn": str})

i18n_local: str = "en"
_I18N_CONTEXT: ContextVar[str] = ContextVar("i18n_context", default=i18n_local)
i18n_config_dict: Dict[str, I18nTypedDict] = {
    "Group": {
        "en": "Group",
        "zh-cn": "组",
    },
    "Name": {
        "en": "Name",
        "zh-cn": "名称",
    },
    "Desc": {
        "en": "Desc",
        "zh-cn": "描述",
    },
    "API": {
        "en": "API",
        "zh-cn": "API",
    },
    "Info": {
        "en": "Info",
        "zh-cn": "信息",
    },
    "Author": {
        "en": "Author",
        "zh-cn": "作者",
    },
    "Status": {
        "en": "Status",
        "zh-cn": "状态",
    },
    "Func": {
        "en": "Func",
        "zh-cn": "函数",
    },
    "Summary": {
        "en": "Summary",
        "zh-cn": "摘要",
    },
    "Path": {"en": "Path", "zh-cn": "路径"},
    "Method": {"en": "Method", "zh-cn": "方法"},
    "Request": {"en": "Request", "zh-cn": "请求"},
    "Response": {"en": "Response", "zh-cn": "响应"},
    "Code": {"en": "Code", "zh-cn": "码"},
    "Media": {"en": "Media", "zh-cn": "媒体"},
    "Data": {"en": "Data", "zh-cn": "数据"},
    "Example": {"en": "Example", "zh-cn": "示例"},
    "Default": {"en": "Default", "zh-cn": "默认"},
    "Other": {"en": "Other", "zh-cn": "其它"},
    "Required": {"en": "Required", "zh-cn": "必填"},
    "Type": {"en": "Type", "zh-cn": "类型"},
    "Param": {"en": "Param", "zh-cn": "参数"},
}


def change_local(lang: str) -> None:
    global i18n_local

    if _I18N_CONTEXT.get(""):
        raise RuntimeError("Can't change i18n_local in i18n context")
    check_i18n_lang(lang)
    i18n_local = lang


def join_i18n(i18n_list: List[str]) -> str:
    if _I18N_CONTEXT.get(i18n_local) == "zh-cn":
        return "".join(i18n_list)
    else:
        return " ".join(i18n_list)


def check_i18n_lang(lang: str) -> None:
    if lang not in ("en", "zh-cn"):
        if not lang.startswith("customer_"):
            raise ValueError(f"Not support {lang}")


class I18nContext(object):
    def __init__(self, i18n_lang: str) -> None:
        check_i18n_lang(i18n_lang)
        self._token: Optional[Token] = None
        self._i18n_lang: str = i18n_lang

    def __enter__(self) -> "I18nContext":
        self._token = _I18N_CONTEXT.set(self._i18n_lang)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._token:
            _I18N_CONTEXT.reset(self._token)
            self._token = None


class I18nHelper(object):
    def __init__(self, name: str):
        # in python 3.10,  can use __set_name__
        self.name: str = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        default: str = " ".join((re.sub(r"(?P<key>[A-Z])", r"_\g<key>", self.__class__.__name__)).split("_"))
        i18n_key: str = _I18N_CONTEXT.get(i18n_local)
        return i18n_config_dict[self.name].get(i18n_key, default)

    @classmethod
    def i(cls, name: str) -> Any:
        return cls(name)


class I18n(object):
    Group: str = I18nHelper.i("Group")
    Name: str = I18nHelper.i("Name")
    Desc: str = I18nHelper.i("Desc")
    API: str = I18nHelper.i("API")
    Info: str = I18nHelper.i("Info")
    Author: str = I18nHelper.i("Author")
    Status: str = I18nHelper.i("Status")
    Func: str = I18nHelper.i("Func")
    Summary: str = I18nHelper.i("Summary")
    Path: str = I18nHelper.i("Path")
    Method: str = I18nHelper.i("Method")
    Request: str = I18nHelper.i("Request")
    Response: str = I18nHelper.i("Response")
    Code: str = I18nHelper.i("Code")
    Media: str = I18nHelper.i("Media")
    Data: str = I18nHelper.i("Data")
    Example: str = I18nHelper.i("Example")
    Default: str = I18nHelper.i("Default")
    Other: str = I18nHelper.i("Other")
    Required: str = I18nHelper.i("Required")
    Type: str = I18nHelper.i("Type")
    Param: str = I18nHelper.i("Param")
