from typing import Any, Dict, Optional

from any_api.openapi.model.openapi import ExternalDocumentationModel, TagModel

__all__ = ["Tag", "ExternalDocumentationModel", "TagModel"]
_tag_dict: Dict[str, dict] = {}


class Tag(object):
    def __init__(self, name: str, desc: str = "", external_docs: Optional["ExternalDocumentationModel"] = None):
        self._name: str = name
        self._desc: str = desc
        self._external_docs: Optional["ExternalDocumentationModel"] = external_docs
        if self._name in _tag_dict and _tag_dict[self._name] != self.to_dict():
            raise KeyError(f"{self._name} tag already exists")

        _tag_dict[self._name] = self.to_dict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def desc(self) -> str:
        return self._desc

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Tag):
            return False
        return other.to_dict() == self.to_dict()

    def to_dict(self) -> dict:
        return {"name": self.name, "desc": self.desc, "external_docs": self._external_docs}

    def to_tag_model(self) -> "TagModel":
        try:
            from any_api.openapi.model.openapi import TagModel
        except ImportError:
            raise RuntimeError("please install any-api")
        return TagModel(name=self.name, description=self.desc, externalDocs=self._external_docs)
