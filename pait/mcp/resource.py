import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from pait.mcp.dispatcher import encode_content


@dataclass
class MCPResource(object):
    uri: str
    handler: Callable
    name: str = ""
    description: str = ""
    mime_type: str = "text/plain"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "uri": self.uri,
            "name": self.name or self.uri,
        }
        if self.description:
            result["description"] = self.description
        if self.mime_type:
            result["mimeType"] = self.mime_type
        return result

    async def read(self) -> Dict[str, Any]:
        value = self.handler()
        if inspect.isawaitable(value):
            value = await value
        return {
            "contents": [
                {
                    "uri": self.uri,
                    "mimeType": self.mime_type,
                    "text": encode_content(value),
                }
            ]
        }


class ResourceRegistry(object):
    def __init__(self) -> None:
        self._resource_dict: Dict[str, MCPResource] = {}

    def resource(
        self,
        uri: str,
        *,
        name: str = "",
        description: str = "",
        mime_type: str = "text/plain",
    ) -> Callable[[Callable], Callable]:
        def decorator(func: Callable) -> Callable:
            self._resource_dict[uri] = MCPResource(
                uri=uri,
                handler=func,
                name=name,
                description=description,
                mime_type=mime_type,
            )
            return func

        return decorator

    def list_resources(self) -> Dict[str, Any]:
        return {"resources": [resource.to_dict() for resource in self._resource_dict.values()]}

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        resource: Optional[MCPResource] = self._resource_dict.get(uri)
        if not resource:
            raise KeyError(f"MCP resource not found: {uri}")
        return await resource.read()
