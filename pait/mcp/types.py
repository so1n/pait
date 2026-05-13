from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Mapping, Optional, Union

if TYPE_CHECKING:
    from pait.mcp.dispatcher import MCPDirectResponse
    from pait.mcp.http import MCPHTTPResponse
    from pait.model.core import PaitCoreModel

MCPArgumentsType = Mapping[str, Any]
MCPMessageType = Mapping[str, Any]
MCPResultType = Dict[str, Any]
ContentEncoderType = Callable[[Any], str]
LoadAppType = Callable[..., Mapping[str, "PaitCoreModel"]]
MCPRouteType = Callable[..., Union[MCPResultType, Awaitable[MCPResultType]]]
ResourceHandlerType = Callable[[], Union[Any, Awaitable[Any]]]
ResourceDecoratorType = Callable[[ResourceHandlerType], ResourceHandlerType]
AsyncDirectDispatcherType = Callable[
    ["PaitCoreModel", Optional[MCPArgumentsType]],
    Awaitable["MCPDirectResponse"],
]
SyncDirectDispatcherType = Callable[
    ["PaitCoreModel", Optional[MCPArgumentsType]],
    "MCPDirectResponse",
]
AsyncHTTPDispatcherType = Callable[
    [Any, "PaitCoreModel", Optional[MCPArgumentsType]],
    Awaitable["MCPHTTPResponse"],
]
SyncHTTPDispatcherType = Callable[
    [Any, "PaitCoreModel", Optional[MCPArgumentsType]],
    "MCPHTTPResponse",
]
