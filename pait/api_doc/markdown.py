import json
from types import CodeType
from typing import Dict, List, Type

from pydantic import BaseModel
from pydantic.fields import Undefined

from pait import field
from pait.api_doc.base_parse import FieldDictType, FieldSchemaTypeDict, PaitBaseParse
from pait.model.core import PaitCoreModel
from pait.model.status import PaitStatus
from pait.util import I18n, gen_example_dict_from_schema, join_i18n


class PaitMd(PaitBaseParse):
    """parse pait dict to md doc"""

    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        title: str = "Pait Doc",
        use_html_details: bool = True,
        enable_inductive_model: bool = True,
    ):
        """
        :param pait_dict: pait dict
        :param title: Md title
        :param use_html_details: Using HTML syntax-related functions
        :param enable_inductive_model: Whether to enable inductive mode (variable use_html_details must be True)
        """
        if enable_inductive_model and not use_html_details:
            raise ValueError("Not support inductive model when `use_html_details` is False")
        self._use_html_details: bool = use_html_details  # some not support markdown in html
        self._enable_inductive_model: bool = enable_inductive_model
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
            |param name|type|default value|example|description|other|
            |---|---|---|---|---|---|
            |age|string|10|user age|example value||
        """
        blank_num_str: str = " " * blank_num
        markdown_text: str = (
            f"{blank_num_str}|{join_i18n([I18n.Param, I18n.Name])}|{I18n.Type}|{I18n.Default}"
            f"|{I18n.Example}|{I18n.Desc}|{I18n.Other}|\n"
        )
        markdown_text += f"{blank_num_str}|---|---|---|---|---|---|\n"
        field_dict_list = sorted(field_dict_list, key=lambda x: x["param_name"])
        for field_info_dict in field_dict_list:
            default = field_info_dict["default"]
            if default is Undefined:
                default = f"**`{I18n.Required}`**"
            type_ = field_info_dict["type"]
            if default is Undefined:
                type_ = f"**`{I18n.Required}`**"
            example_value = ""
            if "other" in field_info_dict:
                example_value = field_info_dict["other"].pop("example", "")
            other_value = ", ".join(
                [f"[`{key}:{value}`]" for key, value in (field_info_dict["other"] or dict()).items()]
            )
            markdown_text += (
                f"{blank_num_str}"
                f"|{field_info_dict['param_name'] or ' '}"
                f"|{type_ or ' '}"
                f"|{default or ' '}"
                f"|{example_value or ' '}"
                f"|{field_info_dict['description'] or ' '}"
                f"|{other_value}"
                f"|\n"
            )
        return markdown_text

    def gen_markdown_text(self) -> str:
        markdown_text: str = f"# {self._title}\n"
        for group in self._group_list:
            # group
            if self._use_html_details and self._enable_inductive_model:
                markdown_text += f"<details><summary>{I18n.Group}: {group}</summary>\n\n"
            else:
                markdown_text += f"## {I18n.Group}: {group}\n\n"
            for pait_model in self._group_pait_dict[group]:
                # func info
                if pait_model.status in (
                    PaitStatus.abnormal,
                    PaitStatus.maintenance,
                    PaitStatus.archive,
                    PaitStatus.abandoned,
                ):
                    markdown_text += f"### {I18n.Name}: ~~{pait_model.operation_id}~~\n\n"
                else:
                    markdown_text += f"### {I18n.Name}: {pait_model.operation_id}\n\n"

                if pait_model.desc:
                    markdown_text += f"\n\n**{I18n.Desc}**:{pait_model.desc}\n\n"

                # func or interface details
                func_code: CodeType = pait_model.func.__code__  # type: ignore
                status_text: str = ""
                if pait_model.status in (PaitStatus.test, PaitStatus.design, PaitStatus.dev, PaitStatus.integration):
                    status_text = f"<font color=#00BFFF>{pait_model.status.value}</font>"
                elif pait_model.status in (PaitStatus.release, PaitStatus.complete):
                    status_text = f"<font color=#32CD32>{pait_model.status.value}</font>"
                elif pait_model.status in (
                    PaitStatus.abnormal,
                    PaitStatus.maintenance,
                    PaitStatus.archive,
                    PaitStatus.abandoned,
                ):
                    status_text = f"<font color=#DC143C>{pait_model.status.value}</font>"
                elif pait_model.status:
                    status_text = f"{pait_model.status.value}"
                markdown_text += f"- {join_i18n([I18n.API, I18n.Info])}\n\n"
                markdown_text += f"{' ' * 4}|{I18n.Author}|{I18n.Status}|{I18n.Func}|{I18n.Summary}|\n"
                markdown_text += f"{' ' * 4}|---|---|---|---|\n"
                markdown_text += (
                    f"{' ' * 4}|{','.join(pait_model.author) if pait_model.author else ''}"
                    f"{' ' * 4}|{status_text}"
                    f'{" " * 4}|<abbr title="file:{pait_model.func_path or func_code.co_filename};'
                    f'line: {func_code.co_firstlineno}">'
                    f"{pait_model.func.__qualname__}</abbr>"
                    f"|{' ' * 4}{pait_model.summary}|\n"
                )

                # request info
                markdown_text += f"- {I18n.Path}: {pait_model.path}\n"
                markdown_text += f"- {I18n.Method}: {','.join(pait_model.method_list)}\n"
                markdown_text += f"- {I18n.Request}:\n"

                all_field_dict: FieldDictType = self._parse_pait_model_to_field_dict(pait_model)
                field_class_list: List[Type[field.BaseField]] = sorted(
                    [i for i in all_field_dict.keys()], key=lambda x: x.get_field_name()
                )
                # request body info
                for field_class in field_class_list:
                    if not issubclass(field_class, field.BaseField):
                        continue
                    field_dict_list = all_field_dict[field_class]
                    markdown_text += f"{' ' * 4}- {field_class.get_field_name().capitalize()} {I18n.Param}\n\n"
                    markdown_text += self.gen_md_param_table(field_dict_list)

                # response info
                markdown_text += f"- {I18n.Response}:\n\n"
                if pait_model.response_model_list:
                    for resp_model_class in pait_model.response_model_list:
                        resp_model = resp_model_class()
                        markdown_text += f"{' ' * 4}- {resp_model.name or resp_model.__class__.__name__}\n\n"
                        markdown_text += f"{' ' * 8}- {join_i18n([I18n.Response, I18n.Info])}\n\n"
                        markdown_text += (
                            f"{' ' * 12}|{join_i18n([I18n.Status, I18n.Code])}|"
                            f"{join_i18n([I18n.Media, I18n.Type])}|{I18n.Desc}|\n"
                        )
                        markdown_text += f"{' ' * 12}|---|---|---|\n"
                        markdown_text += (
                            f"{' ' * 12}|{','.join([str(i) for i in resp_model.status_code])}"
                            f"|{resp_model.media_type}"
                            f"|{resp_model.description}"
                            f"|\n"
                        )
                        if resp_model.header:
                            markdown_text += f"{' ' * 8}- Header\n"
                            markdown_text += f"{' ' * 12}{resp_model.header}\n"

                        if isinstance(resp_model.response_data, type) and issubclass(
                            resp_model.response_data, BaseModel
                        ):
                            markdown_text += f"{' ' * 8}- {join_i18n([I18n.Response, I18n.Data])}\n\n"
                            field_dict_list = self._parse_schema(resp_model.response_data.schema())
                            markdown_text += self.gen_md_param_table(field_dict_list, blank_num=12)
                            markdown_text += (
                                f"{' ' * 8}- " f"{join_i18n([I18n.Example, I18n.Response, 'Json', I18n.Data])} \n\n"
                            )
                            example_dict: dict = gen_example_dict_from_schema(resp_model.response_data.schema())
                            blank_num_str: str = " " * 12
                            json_str: str = "\n".join(
                                [blank_num_str + i for i in json.dumps(example_dict, indent=2).split("\n")]
                            )
                            markdown_text += f"{blank_num_str}```json\n{json_str}\n{blank_num_str}```\n\n"
                markdown_text += "\n"
            if self._use_html_details:
                markdown_text += "</details>"
        return markdown_text
