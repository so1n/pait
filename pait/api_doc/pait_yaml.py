from typing import Any, Dict, Optional

import yaml

from pait.model import PaitCoreModel

from .base_parse import PaitBaseParse  # type: ignore


class PaitYaml(PaitBaseParse):
    def __init__(self, pait_dict: Dict[str, PaitCoreModel], title: str = "Pait Yaml"):
        super().__init__(pait_dict, undefined="Required")

        _pait_dict: Dict[str, Any] = self.gen_dict()
        _pait_dict["title"] = title

        self.content = yaml.dump(_pait_dict)
        self._content_type = ".yaml"
