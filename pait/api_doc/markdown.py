import json
from types import CodeType
from typing import Any, Dict, List

from pydantic.fields import Undefined

from pait.model import PaitCoreModel, PaitStatus

from .base_parse import PaitBaseParse  # type: ignore

json_type_default_value_dict: Dict[str, Any] = {
    "null": None,
    "bool": True,
    "string": "",
    "float": 0.0,
    "integer": 0,
    "object": {},
    "array": [],
}


class PaitMd(PaitBaseParse):
    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        title: str = "Pait Doc",
        use_html_details: bool = True,
    ):
        self._use_html_details: bool = use_html_details  # some not support markdown in html
        self._title: str = title
        super().__init__(pait_dict)

        self.content = self.gen_markdown_text()
        self._content_type = ".md"

    @staticmethod
    def gen_example_json(field_dict_list: List[dict], blank_num: int, indent: int = 2) -> str:
        """
        gen example json by field dict list
        :param field_dict_list:
        :param blank_num: Indent the first character of each line of json
        :param indent: json indent
        :return:
        blank_num: -> .
        indent: -> `
        ....{
        ....``"code": 0,
        ....``"msg": "msg,
        ....}
        """
        blank_num_str: str = " " * blank_num
        example_dict: dict = {}
        for field_dict in field_dict_list:
            sub_dict: dict = example_dict
            key: str = field_dict["param_name"]
            if "." in key:
                key_list: List[str] = key.split(".")
                for sub_key in key_list:
                    key = sub_key
                    if sub_key == key_list[-1]:
                        continue
                    if sub_key not in sub_dict:
                        sub_dict[sub_key] = {}
                    sub_dict = sub_dict[sub_key]
            sub_dict[key] = json_type_default_value_dict[field_dict["type"]]
        json_str: str = f"\n".join([blank_num_str + i for i in json.dumps(example_dict, indent=indent).split("\n")])
        return f"{blank_num_str}```json\n{json_str}\n{blank_num_str}```\n\n"

    @staticmethod
    def gen_md_param_table(field_dict_list: List[dict], blank_num: int = 8) -> str:
        """
        gen param md table
        :param field_dict_list:
        :param blank_num: table str indent
        :return:
            |param name|type|default value|description|other|
            |---|---|---|---|---|
            |age|string|10|user age||
        """
        blank_num_str: str = " " * blank_num
        markdown_text: str = f"{blank_num_str}|param name|type|default value|description|other|\n"
        markdown_text += f"{blank_num_str}|---|---|---|---|---|\n"
        field_dict_list = sorted(field_dict_list, key=lambda x: x["param_name"])
        for field_info_dict in field_dict_list:
            default = field_info_dict["default"]
            if default is Undefined:
                default = "**`Required`**"
            type_ = field_info_dict["type"]
            if default is Undefined:
                type_ = "**`Required`**"
            markdown_text += (
                f"{blank_num_str}"
                f"|{field_info_dict['param_name']}"
                f"|{type_}"
                f"|{default}"
                f"|{field_info_dict['description']}"
                f"|{field_info_dict['other'] or ''}"
                f"|\n"
            )
        return markdown_text

    def gen_markdown_text(self) -> str:
        markdown_text: str = f"# {self._title}\n"
        for group in self._group_list:
            # group
            if self._use_html_details:
                markdown_text += f"<details><summary>Group: {group}</summary>\n\n"
            else:
                markdown_text += f"## Group: {group}\n\n"
            for pait_model in self._group_pait_dict[group]:
                # func info
                markdown_text += f"### Name: {pait_model.operation_id}\n\n"
                status_text: str = ""
                if pait_model.status in (PaitStatus.test, PaitStatus.design, PaitStatus.dev, PaitStatus.integration):
                    status_text = f"<font color=#00BFFF>{pait_model.status.value}</font>"
                elif pait_model.status in (PaitStatus.release, PaitStatus.complete):
                    status_text = f"<font color=#32CD32>{pait_model.status.value}</font>"
                elif pait_model.status in (PaitStatus.abandoned, PaitStatus.abnormal):
                    status_text = f"<font color=#DC143C>{pait_model.status.value}</font>"
                elif pait_model.status:
                    status_text = f"{pait_model.status.value}"

                if pait_model.desc:
                    markdown_text += f"\n\n**Desc**:{pait_model.desc}\n\n"

                # func or interface details
                func_code: CodeType = pait_model.func.__code__
                markdown_text += f"|Author|Status|func|summary|\n"
                markdown_text += f"|---|---|---|---|\n"
                markdown_text += (
                    f"|{','.join(pait_model.author)}"
                    f"|{status_text}"
                    f'|<abbr title="file:{pait_model.func_path or func_code.co_filename};'
                    f'line: {func_code.co_firstlineno}">'
                    f"{pait_model.func.__qualname__}</abbr>"
                    f"|{pait_model.summary}|\n"
                )

                # request info
                markdown_text += f"- Path: {pait_model.path}\n"
                markdown_text += f"- Method: {','.join(pait_model.method_list)}\n"
                markdown_text += f"- Request:\n"

                field_dict: Dict[str, List[Dict[str, Any]]] = self._parse_func_param_to_field_dict(pait_model.func)
                # request body info
                field_key_list: List[str] = sorted(field_dict.keys())
                for field in field_key_list:
                    field_dict_list = field_dict[field]
                    markdown_text += f"{' ' * 4}- {field.capitalize()} Param\n\n"
                    markdown_text += self.gen_md_param_table(field_dict_list)

                # response info
                markdown_text += f"- Response:\n\n"
                if pait_model.response_model_list:
                    for resp_model_class in pait_model.response_model_list:
                        resp_model = resp_model_class()
                        markdown_text += f"{' ' * 4}- {resp_model.name}\n\n"
                        markdown_text += f"{' ' * 8}|status code|media type|description|\n"
                        markdown_text += f"{' ' * 8}|---|---|---|\n"
                        markdown_text += (
                            f"{' ' * 8}|{','.join([str(i) for i in resp_model.status_code])}"
                            f"|{resp_model.media_type}"
                            f"|{resp_model.description}"
                            f"|\n"
                        )
                        if resp_model.header:
                            markdown_text += f"{' ' * 8}- Header\n"
                            markdown_text += f"{' ' * 12}{resp_model.header}\n"
                        if resp_model.response_data:
                            markdown_text += f"{' ' * 8}- Response Data\n\n"
                            field_dict_list = self._parse_schema(resp_model.response_data.schema())
                            markdown_text += self.gen_md_param_table(field_dict_list, blank_num=12)
                            markdown_text += f"{' ' * 8}- Example Response Json Data\n\n"
                            markdown_text += self.gen_example_json(field_dict_list, blank_num=12)
                markdown_text += "\n"
            if self._use_html_details:
                markdown_text += "</details>"
        return markdown_text
