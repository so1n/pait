import json
from typing import Any, Dict, Optional

from pait.model import PaitCoreModel

from .base_parse import PaitBaseParse  # type: ignore


class PaitJson(PaitBaseParse):
    def __init__(
        self,
        pait_dict: Dict[str, PaitCoreModel],
        title: str = "Pait Json",
        filename: Optional[str] = None,
        indent: Optional[int] = None,
    ):
        super().__init__(pait_dict, undefined="Required")

        _pait_dict: Dict[str, Any] = self.gen_dict()
        _pait_dict["title"] = title

        pait_json: str = json.dumps(_pait_dict, indent=indent)
        self.output(filename, pait_json, ".json")
