from typing import Dict

__all__ = ["Tag"]
_tag_dict: Dict[str, str] = {}


class Tag(object):
    def __init__(self, name: str, desc: str = ""):
        self._name: str = name
        self._desc: str = desc
        if self._name in _tag_dict and _tag_dict[self._name] != self._desc:
            raise KeyError(f"{self._name} tag already exists")

        _tag_dict[self._name] = self.desc

    @property
    def name(self) -> str:
        return self._name

    @property
    def desc(self) -> str:
        return self._desc
