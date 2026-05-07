import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from pait.mcp.dispatcher import encode_content


@dataclass
class MCPResource(object):
    """MCP resource metadata and read handler."""

    uri: str
    handler: Callable
    name: str = ""
    description: str = ""
    mime_type: str = "text/plain"

    def to_dict(self) -> Dict[str, Any]:
        """Return the MCP ``Resource`` representation."""
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
        """Read resource content from a sync or async handler."""
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

    def read_sync(self) -> Dict[str, Any]:
        """Read resource content from a synchronous handler."""
        value = self.handler()
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
    """Registry for decorator-defined MCP resources."""

    def __init__(self) -> None:
        """Create an empty resource registry."""
        self._resource_dict: Dict[str, MCPResource] = {}

    def resource(
        self,
        uri: str,
        *,
        name: str = "",
        description: str = "",
        mime_type: str = "text/plain",
    ) -> Callable[[Callable], Callable]:
        """Return a decorator that registers an MCP resource handler."""

        def decorator(func: Callable) -> Callable:
            """Register ``func`` as the handler for ``uri``."""
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
        """Return MCP ``resources/list`` payload."""
        return {"resources": [resource.to_dict() for resource in self._resource_dict.values()]}

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI asynchronously."""
        resource: Optional[MCPResource] = self._resource_dict.get(uri)
        if not resource:
            raise KeyError(f"MCP resource not found: {uri}")
        return await resource.read()

    def read_resource_sync(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI synchronously."""
        resource: Optional[MCPResource] = self._resource_dict.get(uri)
        if not resource:
            raise KeyError(f"MCP resource not found: {uri}")
        return resource.read_sync()
