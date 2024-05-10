from typing import Any, Dict, Optional

from any_api.openapi.model.openapi import ExternalDocumentationModel, TagModel

__all__ = ["Tag", "ExternalDocumentationModel", "TagModel"]
_tag_dict: Dict[str, dict] = {}


class Tag(object):
    def __init__(
        self,
        name: str,
        desc: str = "",
        external_docs: Optional["ExternalDocumentationModel"] = None,
        openapi_include: bool = True,
        label: Optional[str] = None,
    ):
        """
        :param name: tag name
        :param desc: tag description
        :param external_docs: external docs
        :param openapi_include: Whether to include in openapi
        :param label: tag label
        """
        self._name: str = name
        self._desc: str = desc
        self._external_docs: Optional["ExternalDocumentationModel"] = external_docs
        self._openapi_include: bool = openapi_include
        self._label: Optional[str] = label

        if self._name in _tag_dict and _tag_dict[self._name] != self.to_dict():
            raise KeyError(f"{self._name} tag already exists")

        _tag_dict[self._name] = self.to_dict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def desc(self) -> str:
        return self._desc

    @property
    def external_docs(self) -> Optional["ExternalDocumentationModel"]:
        return self._external_docs

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def openapi_include(self) -> bool:
        return self._openapi_include

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Tag):
            return False
        return other.to_dict() == self.to_dict()

    def __repr__(self) -> str:
        return f"<{__name__}.{self.__class__.__name__}>(name='{self.name}')"

    def to_dict(self) -> dict:
        return {"name": self.name, "desc": self.desc, "external_docs": self._external_docs}

    def to_tag_model(self) -> "TagModel":
        return TagModel(name=self.name, description=self.desc, externalDocs=self._external_docs)
