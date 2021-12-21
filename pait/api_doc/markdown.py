import json
from types import CodeType
from typing import Dict, List

from pydantic.fields import Undefined

from pait import field
from pait.model.core import PaitCoreModel
from pait.model.status import PaitStatus
from pait.util import gen_example_dict_from_schema

from .base_parse import FieldDictType, FieldSchemaTypeDict, PaitBaseParse  # type: ignore


class PaitMd(PaitBaseParse):
    """parse pait dict to md doc"""

    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        title: str = "Pait Doc",
        use_html_details: bool = True,
    ):
        """
        :param pait_dict: pait dict
        :param title: Md title
        :param use_html_details: Using HTML syntax-related functions
        """
        self._use_html_details: bool = use_html_details  # some not support markdown in html
        self._title: str = title

        super().__init__(pait_dict)

        self.content = self.gen_markdown_text()
        self._content_type = ".md"

    @staticmethod
    def gen_md_param_table(field_dict_list: List[FieldSchemaTypeDict], blank_num: int = 8) -> str:
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
                func_code: CodeType = pait_model.func.__code__  # type: ignore
                markdown_text += "|Author|Status|func|summary|\n"
                markdown_text += "|---|---|---|---|\n"
                markdown_text += (
                    f"|{','.join(pait_model.author) if pait_model.author else ''}"
                    f"|{status_text}"
                    f'|<abbr title="file:{pait_model.func_path or func_code.co_filename};'
                    f'line: {func_code.co_firstlineno}">'
                    f"{pait_model.func.__qualname__}</abbr>"
                    f"|{pait_model.summary}|\n"
                )

                # request info
                markdown_text += f"- Path: {pait_model.path}\n"
                markdown_text += f"- Method: {','.join(pait_model.method_list)}\n"
                markdown_text += "- Request:\n"

                field_dict: FieldDictType = self._parse_func_param_to_field_dict(pait_model.func)
                for pre_depend in pait_model.pre_depend_list:
                    for field_class, field_dict_list in self._parse_func_param_to_field_dict(pre_depend).items():
                        if field_class not in field_dict:
                            field_dict[field_class] = field_dict_list
                        else:
                            field_dict[field_class].extend(field_dict_list)

                # gen key, class can not sort, so replace to instance
                field_key_list: List[field.BaseField] = sorted([i() for i in field_dict.keys()])
                # request body info
                for field_instance in field_key_list:
                    field_class = field_instance.__class__
                    if not issubclass(field_class, field.BaseField):
                        continue
                    field_dict_list = field_dict[field_class]
                    markdown_text += f"{' ' * 4}- {field_class.cls_lower_name().capitalize()} Param\n\n"
                    markdown_text += self.gen_md_param_table(field_dict_list)

                # response info
                markdown_text += "- Response:\n\n"
                if pait_model.response_model_list:
                    for resp_model_class in pait_model.response_model_list:
                        resp_model = resp_model_class()
                        markdown_text += f"{' ' * 4}- {resp_model.name or resp_model.__class__.__name__}\n\n"
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
                            example_dict: dict = gen_example_dict_from_schema(resp_model.response_data.schema(), False)
                            blank_num_str: str = " " * 12
                            json_str: str = "\n".join(
                                [blank_num_str + i for i in json.dumps(example_dict, indent=2).split("\n")]
                            )
                            markdown_text += f"{blank_num_str}```json\n{json_str}\n{blank_num_str}```\n\n"
                markdown_text += "\n"
            if self._use_html_details:
                markdown_text += "</details>"
        return markdown_text
