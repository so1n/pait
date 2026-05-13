import inspect
from dataclasses import dataclass
from typing import Dict, Optional

from pait.mcp.dispatcher import encode_content
from pait.mcp.types import ContentEncoderType, MCPResultType, ResourceDecoratorType, ResourceHandlerType


@dataclass
class MCPResource(object):
    """MCP resource metadata and read handler."""

    uri: str
    handler: ResourceHandlerType
    name: str = ""
    description: str = ""
    mime_type: str = "text/plain"
    content_encoder: ContentEncoderType = encode_content

    def to_dict(self) -> MCPResultType:
        """Return the MCP ``Resource`` representation."""
        result: MCPResultType = {
            "uri": self.uri,
            "name": self.name or self.uri,
        }
        if self.description:
            result["description"] = self.description
        if self.mime_type:
            result["mimeType"] = self.mime_type
        return result

    async def read(self) -> MCPResultType:
        """Read resource content from a sync or async handler."""
        value = self.handler()
        if inspect.isawaitable(value):
            value = await value
        return {
            "contents": [
                {
                    "uri": self.uri,
                    "mimeType": self.mime_type,
                    "text": self.content_encoder(value),
                }
            ]
        }

    def read_sync(self) -> MCPResultType:
        """Read resource content from a synchronous handler."""
        value = self.handler()
        return {
            "contents": [
                {
                    "uri": self.uri,
                    "mimeType": self.mime_type,
                    "text": self.content_encoder(value),
                }
            ]
        }


class ResourceRegistry(object):
    """Registry for decorator-defined MCP resources."""

    def __init__(self, content_encoder: ContentEncoderType = encode_content) -> None:
        """Create an empty resource registry."""
        self._resource_dict: Dict[str, MCPResource] = {}
        self.content_encoder = content_encoder

    def resource(
        self,
        uri: str,
        *,
        name: str = "",
        description: str = "",
        mime_type: str = "text/plain",
    ) -> ResourceDecoratorType:
        """Return a decorator that registers an MCP resource handler."""

        def decorator(func: ResourceHandlerType) -> ResourceHandlerType:
            """Register ``func`` as the handler for ``uri``."""
            self._resource_dict[uri] = MCPResource(
                uri=uri,
                handler=func,
                name=name,
                description=description,
                mime_type=mime_type,
                content_encoder=self.content_encoder,
            )
            return func

        return decorator

    def list_resources(self) -> MCPResultType:
        """Return MCP ``resources/list`` payload."""
        return {"resources": [resource.to_dict() for resource in self._resource_dict.values()]}

    async def read_resource(self, uri: str) -> MCPResultType:
        """Read a resource by URI asynchronously."""
        resource: Optional[MCPResource] = self._resource_dict.get(uri)
        if not resource:
            raise KeyError(f"MCP resource not found: {uri}")
        return await resource.read()

    def read_resource_sync(self, uri: str) -> MCPResultType:
        """Read a resource by URI synchronously."""
        resource: Optional[MCPResource] = self._resource_dict.get(uri)
        if not resource:
            raise KeyError(f"MCP resource not found: {uri}")
        return resource.read_sync()
