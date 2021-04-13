import json
from typing import Any, Dict, Optional

from .base_parse import PaitBaseParse


class PaitJson(PaitBaseParse):
    def __init__(
            self, app_name: str, title: str = "Pait Json", filename: Optional[str] = None, indent: Optional[int] = None
    ):
        super().__init__(app_name, undefined="Required")

        pait_dict: Dict[str, Any] = self.gen_dict()
        pait_dict["title"] = title

        pait_json: str = json.dumps(pait_dict, indent=indent)
        self.output(filename, pait_json, ".json")
